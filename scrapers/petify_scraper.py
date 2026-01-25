#!/usr/bin/env python3
"""
Petify Scraper - Fixes seller_name extraction bug
The original data had "Since J" etc. instead of actual seller names.
"""

import asyncio
import csv
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "Input" / "Raw CSVs"
BASE_URL = "https://www.petify.uk"
LISTINGS_URL = f"{BASE_URL}/for-sale/dogs?page="


async def get_listing_urls(page, max_pages=50):
    """Scrape all listing URLs from paginated results"""
    urls = []

    for page_num in range(1, max_pages + 1):
        print(f"  Scanning page {page_num}...", end=" ")

        await page.goto(f"{LISTINGS_URL}{page_num}", wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1000)

        # Find all listing links - Petify uses cards with links to /for-sale/breed/location/id
        links = await page.query_selector_all('a[href*="/for-sale/"][href*="-dogs/"]')
        page_urls = []

        for link in links:
            href = await link.get_attribute('href')
            if href and re.search(r'/\d+$', href):  # URLs ending in ID number
                full_url = href if href.startswith('http') else f"{BASE_URL}{href}"
                if full_url not in urls:
                    page_urls.append(full_url)

        urls.extend(page_urls)
        print(f"found {len(page_urls)} listings (total: {len(urls)})")

        if len(page_urls) == 0:
            print("  No more listings found, stopping.")
            break

        await asyncio.sleep(0.5)

    return urls


async def scrape_listing(page, url):
    """Scrape a single Petify listing"""
    listing = {
        'id': url.split('/')[-1],
        'url': url,
        'platform': 'petify',
        'scraped_at': datetime.now().isoformat()
    }

    try:
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1000)

        # Get full page text for regex matching
        body_text = await page.inner_text('body')

        # Title
        try:
            h1 = await page.query_selector('h1')
            if h1:
                listing['title'] = await h1.inner_text()
        except:
            pass

        # Breed from URL
        breed_match = re.search(r'/for-sale/([^/]+)-dogs/', url)
        if breed_match:
            listing['breed'] = breed_match.group(1).replace('-', ' ').title()

        # Price - look for £ followed by number
        price_match = re.search(r'£([\d,]+)', body_text)
        if price_match:
            listing['price'] = price_match.group(1).replace(',', '')

        # Location from URL
        loc_match = re.search(r'-dogs/([^/]+)/\d+$', url)
        if loc_match:
            listing['location'] = loc_match.group(1).replace('-', ' ').title()

        # Age - various formats
        age_patterns = [
            r'(\d+)\s*weeks?\s*old',
            r'(\d+)\s*months?\s*old',
            r'Age[:\s]*(\d+\s*(?:weeks?|months?))',
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, body_text, re.I)
            if age_match:
                listing['age'] = age_match.group(1) if 'weeks' in age_match.group(0).lower() or 'months' in age_match.group(0).lower() else f"{age_match.group(1)} weeks"
                break

        # Ready to leave
        rtl_patterns = [
            r'Ready to leave[:\s]*(Now|Immediately)',
            r'Ready to leave[:\s]*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+)',
            r'Ready[:\s]*(Now)',
        ]
        for pattern in rtl_patterns:
            rtl_match = re.search(pattern, body_text, re.I)
            if rtl_match:
                listing['ready_to_leave'] = rtl_match.group(1)
                break

        # Males/Females available
        males_match = re.search(r'(\d+)\s*[Mm]ale', body_text)
        females_match = re.search(r'(\d+)\s*[Ff]emale', body_text)
        if males_match:
            listing['males_available'] = int(males_match.group(1))
        if females_match:
            listing['females_available'] = int(females_match.group(1))

        # Posted date - look for "X days ago" or date
        posted_patterns = [
            r'(\d+)\s*days?\s*ago',
            r'(\d+)\s*hours?\s*ago',
            r'Posted[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        for pattern in posted_patterns:
            posted_match = re.search(pattern, body_text, re.I)
            if posted_match:
                listing['posted_ago'] = posted_match.group(0)
                break

        # Seller type (Domestic Breeder, Licensed Breeder, etc.)
        seller_type_match = re.search(r'(Licensed Breeder|Domestic Breeder|Private Seller|Rehome)', body_text, re.I)
        if seller_type_match:
            listing['seller_type'] = seller_type_match.group(1)

        # SELLER NAME - This is the critical fix!
        # Look for the seller name which appears after the avatar/profile section
        # Try multiple patterns to find the actual name

        # Pattern 1: Look for name near "Member since" but BEFORE the "Since"
        # The page structure typically shows: [Avatar] [Name] [Member since Month Year]

        # Try to get seller info from the seller card/section
        seller_section = await page.query_selector('[class*="seller"], [class*="breeder"], [class*="profile"]')
        if seller_section:
            seller_text = await seller_section.inner_text()
            # The name is usually the first line before "Member since" or "Since"
            lines = [l.strip() for l in seller_text.split('\n') if l.strip()]
            for i, line in enumerate(lines):
                # Skip common non-name lines
                if line.lower() in ['domestic breeder', 'licensed breeder', 'private seller', 'rehome']:
                    continue
                if line.lower().startswith('since ') or line.lower().startswith('member since'):
                    continue
                if re.match(r'^[A-Z][a-z]+\s+[A-Z]$', line) or re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', line):
                    # Looks like a name (e.g., "Charli K" or "John Smith")
                    listing['seller_name'] = line
                    break

        # Fallback: Try regex on body text
        if 'seller_name' not in listing:
            # Look for pattern like initials in a circle followed by name
            name_patterns = [
                r'(?:Posted by|Seller|Breeder)[:\s]*([A-Z][a-z]+(?:\s+[A-Z]\.?)?)',
                r'Contact\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?)',
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, body_text)
                if name_match:
                    name = name_match.group(1).strip()
                    if name.lower() not in ['the', 'this', 'seller', 'breeder', 'domestic', 'licensed']:
                        listing['seller_name'] = name
                        break

        # Member since - capture full month year
        member_match = re.search(r'(?:Member\s+)?[Ss]ince\s+([A-Za-z]+\s+\d{4})', body_text)
        if member_match:
            listing['member_since'] = member_match.group(1)

        # Health/compliance checks
        listing['kc_registered'] = bool(re.search(r'KC Registered|Kennel Club', body_text, re.I))
        listing['microchipped'] = bool(re.search(r'Microchipped', body_text, re.I))
        listing['vaccinated'] = bool(re.search(r'Vaccinated', body_text, re.I))
        listing['wormed'] = bool(re.search(r'Wormed', body_text, re.I))
        listing['health_checked'] = bool(re.search(r'Health Checked|Vet Checked', body_text, re.I))
        listing['id_verified'] = bool(re.search(r'ID Verified', body_text, re.I))

    except Exception as e:
        listing['error'] = str(e)

    return listing


async def main():
    print("=" * 60)
    print("PETIFY SCRAPER - Fixing seller_name extraction")
    print("=" * 60)

    listings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # Phase 1: Collect all listing URLs
        print("\nPhase 1: Collecting listing URLs...")
        urls = await get_listing_urls(page)
        print(f"\nFound {len(urls)} unique listings")

        # Save URLs
        with open(OUTPUT_DIR / 'petify_urls.txt', 'w') as f:
            f.write('\n'.join(urls))

        # Phase 2: Scrape each listing
        print(f"\nPhase 2: Scraping {len(urls)} listings...")

        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url.split('/')[-1]}", end=' ')

            listing = await scrape_listing(page, url)
            listings.append(listing)

            seller = listing.get('seller_name', 'NO_NAME')
            if 'error' in listing:
                print(f"ERROR: {listing['error'][:30]}")
            else:
                print(f"-> {seller}")

            # Save progress every 50 listings
            if i % 50 == 0:
                save_results(listings)
                print(f"  [Saved {i} listings]")

            await asyncio.sleep(0.5)

        await browser.close()

    # Save final results
    save_results(listings)

    # Summary
    with_name = sum(1 for l in listings if l.get('seller_name'))
    with_price = sum(1 for l in listings if l.get('price'))
    errors = sum(1 for l in listings if l.get('error'))

    print(f"\n{'=' * 60}")
    print(f"DONE! {len(listings)} listings scraped")
    if len(listings) > 0:
        print(f"  With seller_name: {with_name} ({100*with_name/len(listings):.0f}%)")
        print(f"  With price: {with_price} ({100*with_price/len(listings):.0f}%)")
        print(f"  Errors: {errors}")
        print(f"\nSaved to: {OUTPUT_DIR / 'petify_data_v3.csv'}")
    else:
        print("  No listings were found. The website structure may have changed.")


def save_results(listings):
    """Save listings to CSV"""
    cols = [
        'id', 'title', 'breed', 'price', 'location',
        'date_of_birth', 'age', 'ready_to_leave',
        'males_available', 'females_available',
        'posted_ago', 'posted_date',
        'seller_type', 'seller_name', 'member_since',
        'kc_registered', 'microchipped', 'vaccinated', 'wormed',
        'health_checked', 'id_verified',
        'views', 'url', 'scraped_at', 'error'
    ]

    with open(OUTPUT_DIR / 'petify_data_v3.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(listings)


if __name__ == "__main__":
    asyncio.run(main())
