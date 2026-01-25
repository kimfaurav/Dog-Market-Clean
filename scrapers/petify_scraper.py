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

# Popular breeds to scrape
BREEDS = [
    'french-bulldog', 'labrador-retriever', 'cockapoo', 'cocker-spaniel',
    'golden-retriever', 'german-shepherd', 'cavapoo', 'dachshund',
    'miniature-dachshund', 'english-bulldog', 'pug', 'shih-tzu',
    'chihuahua', 'border-collie', 'yorkshire-terrier', 'maltese',
    'pomeranian', 'jack-russell', 'staffordshire-bull-terrier', 'labradoodle',
    'rottweiler', 'siberian-husky', 'cane-corso', 'american-bully'
]


async def get_location_urls(page, breed):
    """Get all location URLs for a specific breed"""
    url = f"{BASE_URL}/puppies-and-dogs-for-sale/{breed}"
    await page.goto(url, wait_until='networkidle', timeout=30000)
    await page.wait_for_timeout(1000)

    # Find location links (pattern: /puppies-and-dogs-for-sale/{breed}/in/{location}/{id})
    links = await page.query_selector_all(f'a[href*="/puppies-and-dogs-for-sale/{breed}/in/"]')
    location_urls = []

    for link in links:
        href = await link.get_attribute('href')
        if href and re.search(r'/in/[^/]+/\d+$', href):
            full_url = href if href.startswith('http') else f"{BASE_URL}{href}"
            if full_url not in location_urls:
                location_urls.append(full_url)

    return location_urls


async def get_listings_from_location(page, location_url):
    """Get individual listing URLs from a breed+location page"""
    await page.goto(location_url, wait_until='networkidle', timeout=30000)
    await page.wait_for_timeout(2000)  # Extra wait for JS content

    # Find listing links (pattern: /for-sale/{breed}-dogs/{location}/{id})
    links = await page.query_selector_all('a[href*="/for-sale/"][href*="-dogs/"]')
    listing_urls = []

    for link in links:
        href = await link.get_attribute('href')
        if href and re.search(r'-dogs/[^/]+/\d+$', href):
            full_url = href if href.startswith('http') else f"{BASE_URL}{href}"
            if full_url not in listing_urls:
                listing_urls.append(full_url)

    return listing_urls


async def get_listing_urls(page, max_listings=500):
    """Scrape listing URLs by navigating through breed and location pages"""
    all_urls = set()

    for breed in BREEDS:
        print(f"  Scanning breed: {breed}...", end=" ")

        try:
            # Get location URLs for this breed
            location_urls = await get_location_urls(page, breed)
            breed_listings = 0

            # Visit each location to get individual listings
            for loc_url in location_urls[:10]:  # Limit locations per breed
                listing_urls = await get_listings_from_location(page, loc_url)
                new_urls = [u for u in listing_urls if u not in all_urls]
                all_urls.update(new_urls)
                breed_listings += len(new_urls)

                if len(all_urls) >= max_listings:
                    print(f"found {breed_listings} (total: {len(all_urls)}) - reached limit")
                    return list(all_urls)

                await asyncio.sleep(0.3)

            print(f"found {breed_listings} (total: {len(all_urls)})")

        except Exception as e:
            print(f"error: {str(e)[:30]}")

        await asyncio.sleep(0.5)

    return list(all_urls)


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

        # SELLER INITIALS - Petify only shows initials, not full names (privacy feature)
        # Look for initials in the avatar element
        try:
            avatar = await page.query_selector('[class*="avatar"] span, [class*="initials"]')
            if avatar:
                initials = await avatar.inner_text()
                initials = initials.strip()
                # Validate it looks like initials (1-3 uppercase letters)
                if initials and re.match(r'^[A-Z]{1,3}$', initials):
                    listing['seller_initials'] = initials
        except:
            pass

        # Fallback: extract initials from profile section text
        if 'seller_initials' not in listing:
            profile = await page.query_selector('[class*="profile"]')
            if profile:
                profile_text = await profile.inner_text()
                # Look for standalone 1-3 letter patterns that look like initials
                initials_match = re.search(r'\b([A-Z]{2,3})\b', profile_text)
                if initials_match:
                    listing['seller_initials'] = initials_match.group(1)

        # Member since - capture full month year
        member_match = re.search(r'[Ss]ince\s+([A-Za-z]+\s+\d{4})', body_text)
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

            seller = listing.get('seller_initials', 'NO_INITIALS')
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
    with_initials = sum(1 for l in listings if l.get('seller_initials'))
    with_price = sum(1 for l in listings if l.get('price'))
    with_member_since = sum(1 for l in listings if l.get('member_since'))
    errors = sum(1 for l in listings if l.get('error'))

    print(f"\n{'=' * 60}")
    print(f"DONE! {len(listings)} listings scraped")
    if len(listings) > 0:
        print(f"  With seller_initials: {with_initials} ({100*with_initials/len(listings):.0f}%)")
        print(f"  With member_since: {with_member_since} ({100*with_member_since/len(listings):.0f}%)")
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
        'seller_type', 'seller_initials', 'member_since',
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
