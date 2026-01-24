#!/usr/bin/env python3
"""
Gundogs Direct Scraper - Using Playwright for JavaScript rendering
Captures: date_of_birth, ready_to_leave, price, location, health info, etc.
"""

import asyncio
import json
import csv
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "Input" / "Raw CSVs"
BASE_URL = "https://gundogsdirect.co.uk"
LISTINGS_URL = f"{BASE_URL}/dogs-for-sale?map=off&page="


async def get_listing_urls(page, max_pages=30):
    """Scrape all listing URLs from paginated results"""
    urls = []

    for page_num in range(1, max_pages + 1):
        print(f"  Scanning page {page_num}...", end=" ")

        await page.goto(f"{LISTINGS_URL}{page_num}", wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1000)

        # Find all listing links
        links = await page.query_selector_all('a[href*="/dogs-for-sale/"]')
        page_urls = []

        for link in links:
            href = await link.get_attribute('href')
            if href and re.search(r'/\d+$', href):  # URLs ending in ID number
                full_url = href if href.startswith('http') else f"{BASE_URL}{href}"
                if full_url not in urls:
                    page_urls.append(full_url)

        urls.extend(page_urls)
        print(f"found {len(page_urls)} listings (total: {len(urls)})")

        # Check if we've reached the end
        if len(page_urls) == 0:
            break

        await asyncio.sleep(0.5)

    return urls


async def scrape_listing(page, url):
    """Scrape a single Gundogs Direct listing"""
    listing = {
        'url': url,
        'id': url.split('/')[-1],
        'platform': 'gundogs_direct',
        'scraped_at': datetime.now().isoformat()
    }

    try:
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1000)

        body_text = await page.inner_text('body')

        # Title
        try:
            h1 = await page.query_selector('h1')
            if h1:
                listing['title'] = await h1.inner_text()
        except:
            pass

        # Breed from URL
        breed_match = re.search(r'/dogs-for-sale/([^/]+)-for-sale/', url)
        if breed_match:
            listing['breed'] = breed_match.group(1).replace('-', ' ').title()

        # Price
        price_match = re.search(r'£([\d,]+(?:\.\d{2})?)', body_text)
        if price_match:
            listing['price'] = price_match.group(1).replace(',', '').replace('.00', '')

        # Advert ID
        id_match = re.search(r'Advert ID[:\s]*(\d+)', body_text)
        if id_match:
            listing['ad_id'] = id_match.group(1)

        # Posted Date - format: "01-01-2026" with label "Date Posted:"
        posted_patterns = [
            r'Date\s*Posted\s*[:\s]*(\d{2}-\d{2}-\d{4})',
            r'Posted\s*Date\s*[:\s]*(\d{2}-\d{2}-\d{4})',
            r'Posted\s*[:\s]*(\d{2}-\d{2}-\d{4})',
            r'Listed\s*[:\s]*(\d{2}-\d{2}-\d{4})',
        ]
        for pattern in posted_patterns:
            posted_match = re.search(pattern, body_text, re.I)
            if posted_match:
                listing['posted_date'] = posted_match.group(1)
                try:
                    dt = datetime.strptime(posted_match.group(1), '%d-%m-%Y')
                    listing['posted_date_iso'] = dt.strftime('%Y-%m-%d')
                except:
                    pass
                break

        # Last Updated - format: "24-01-2026"
        updated_match = re.search(r'Last\s*Updated\s*[:\s]*(\d{2}-\d{2}-\d{4})', body_text, re.I)
        if updated_match:
            listing['last_updated'] = updated_match.group(1)

        # Litter Size - format: "7 pups in the litter" or "Litter Size: 7"
        litter_patterns = [
            r'(\d+)\s*pups?\s*in\s*the\s*litter',
            r'Litter\s*Size\s*[:\s]*(\d+)',
        ]
        for pattern in litter_patterns:
            litter_match = re.search(pattern, body_text, re.I)
            if litter_match:
                listing['litter_size'] = int(litter_match.group(1))
                break

        # Available puppies - format: "2 dogs Available" or "Available: 2"
        available_patterns = [
            r'(\d+)\s*(?:dogs?|puppies?|pups?)\s*[Aa]vailable',
            r'[Aa]vailable\s*[:\s]*(\d+)',
        ]
        for pattern in available_patterns:
            available_match = re.search(pattern, body_text, re.I)
            if available_match:
                listing['available_puppies'] = int(available_match.group(1))
                break

        # Date of Birth - format: "15 Dec 2025" or "15th December 2025"
        dob_patterns = [
            r'Date\s*of\s*Birth\s*[:\s"\']*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})',
            r'Date\s*of\s*Birth\s*[:\s"\']*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Date\s*of\s*Birth\s*[:\s]*(\d{2}-\d{2}-\d{4})',
            r'DOB\s*[:\s]*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        ]
        for pattern in dob_patterns:
            dob_match = re.search(pattern, body_text, re.I)
            if dob_match:
                listing['date_of_birth'] = dob_match.group(1).strip()
                break

        # Ready to Leave - format: "16th February 2026" or "Now" or in description
        rtl_patterns = [
            r'Ready\s*to\s*Leave\s*[:\s"\']*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})',
            r'Ready\s*to\s*Leave\s*[:\s"\']*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Ready\s*to\s*Leave\s*[:\s"\']*(Now|Immediately)',
            r'ready\s+to\s+leave\s+(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+)',  # in description
            r'ready\s+to\s+go\s+(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+)',
            r'available\s+(?:from\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+)',
            r'can\s+leave\s+(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+)',
        ]
        for pattern in rtl_patterns:
            rtl_match = re.search(pattern, body_text, re.I)
            if rtl_match:
                listing['ready_to_leave'] = rtl_match.group(1).strip()
                break

        # Current Age - various formats
        age_patterns = [
            r'Current\s*Age\s*[:\s]*(\d+\s*years?,?\s*\d+\s*months?,?\s*\d+\s*days?)',
            r'Age\s*[:\s]*(\d+\s*weeks?)',
            r'(\d+)\s*weeks?\s*old',
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, body_text, re.I)
            if age_match:
                listing['age'] = age_match.group(1).strip()
                break

        # Location - format: "Battle, UK" or with county
        location_patterns = [
            r'Location\s*[:\s"\']*([A-Za-z][A-Za-z\s\-\']+),?\s*UK',
            r'County\s*[:\s"\']*([A-Za-z][A-Za-z\s\-\']+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*UK',
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, body_text)
            if location_match:
                listing['location'] = location_match.group(1).strip()
                break

        # Also try to get county separately
        county_match = re.search(r'County\s*[:\s"\']*([A-Za-z][A-Za-z\s\-\']+)', body_text)
        if county_match:
            listing['county'] = county_match.group(1).strip()

        # Seller info - look for seller name in "Seller Details" section
        # The format is: "Name: C&S Tompsett" followed by "Verified Breeder:"
        seller_patterns = [
            r'Name\s*[:\s]*([A-Za-z0-9][A-Za-z0-9\s&\-\'\.]+?)\s*(?:Verified\s*Breeder|Member\s*Since|Posted\s*Adverts)',
            r'Seller\s*Details.*?Name\s*[:\s]*([A-Za-z0-9][A-Za-z0-9\s&\-\'\.]+)',
        ]
        for pattern in seller_patterns:
            seller_match = re.search(pattern, body_text, re.I | re.DOTALL)
            if seller_match:
                name = seller_match.group(1).strip()
                # Filter out common false positives
                if name.lower() not in ['yes', 'no', 'the', 'this', 'name', 'seller', 'details']:
                    listing['seller_name'] = name
                    break

        member_match = re.search(r'Member\s*Since\s*[:\s]*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})', body_text, re.I)
        if member_match:
            listing['member_since'] = member_match.group(1)

        # Verified breeder
        listing['verified_breeder'] = 'verified breeder: yes' in body_text.lower() or 'verified breeder</span>' in body_text.lower()

        # Health info
        listing['health_checked'] = bool(re.search(r'Health Checked[:\s]*Yes', body_text, re.I))
        listing['hip_scored'] = bool(re.search(r'Hip Dysplasia[:\s]*Yes', body_text, re.I))
        listing['elbow_scored'] = bool(re.search(r'Elbow Dysplasia[:\s]*Yes', body_text, re.I))
        listing['eye_tested'] = bool(re.search(r'Eye Screening[:\s]*Yes', body_text, re.I))
        listing['vaccinated'] = bool(re.search(r'Vaccinations[:\s]*Yes', body_text, re.I))
        listing['microchipped'] = bool(re.search(r'Microchipped[:\s]*Yes', body_text, re.I))
        listing['wormed'] = bool(re.search(r'Worm.*Treated[:\s]*Yes', body_text, re.I))
        listing['kc_registered'] = bool(re.search(r'KC Registered[:\s]*Yes', body_text, re.I))

        # Original breeder
        listing['original_breeder'] = bool(re.search(r'Original Breeder[:\s]*Yes', body_text, re.I))

        # Viewable with mother
        listing['viewable_with_mother'] = bool(re.search(r'Viewable with Mother[:\s]*Yes', body_text, re.I))

    except Exception as e:
        listing['error'] = str(e)

    return listing


async def main():
    print("=" * 60)
    print("GUNDOGS DIRECT SCRAPER")
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

        # Save URLs for resumability
        with open(OUTPUT_DIR / 'gundogs_direct_urls.txt', 'w') as f:
            f.write('\n'.join(urls))

        # Phase 2: Scrape each listing
        print(f"\nPhase 2: Scraping {len(urls)} listings...")

        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url.split('/')[-1]}", end=' ')

            listing = await scrape_listing(page, url)
            listings.append(listing)

            if 'error' in listing:
                print(f"error: {listing['error'][:30]}")
            elif listing.get('date_of_birth'):
                print(f"DOB: {listing['date_of_birth']}")
            else:
                print("ok")

            # Save progress every 50 listings
            if i % 50 == 0:
                with open(OUTPUT_DIR / 'gundogs_direct_data.json', 'w') as f:
                    json.dump(listings, f, indent=2)
                print(f"  Saved {i} listings")

            await asyncio.sleep(0.5)  # Polite delay

        await browser.close()

    # Save final results
    with open(OUTPUT_DIR / 'gundogs_direct_data.json', 'w') as f:
        json.dump(listings, f, indent=2)

    # Save CSV
    cols = [
        'id', 'ad_id', 'title', 'breed', 'price', 'location', 'county',
        'date_of_birth', 'age', 'ready_to_leave',
        'litter_size', 'available_puppies',
        'posted_date', 'posted_date_iso', 'last_updated',
        'seller_name', 'member_since', 'verified_breeder',
        'health_checked', 'hip_scored', 'elbow_scored', 'eye_tested',
        'vaccinated', 'microchipped', 'wormed', 'kc_registered',
        'original_breeder', 'viewable_with_mother',
        'platform', 'url', 'scraped_at', 'error'
    ]

    with open(OUTPUT_DIR / 'gundogs_direct_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(listings)

    # Summary
    with_dob = sum(1 for l in listings if l.get('date_of_birth'))
    with_rtl = sum(1 for l in listings if l.get('ready_to_leave'))
    with_price = sum(1 for l in listings if l.get('price'))
    kc_reg = sum(1 for l in listings if l.get('kc_registered'))
    errors = sum(1 for l in listings if l.get('error'))

    print(f"\n{'=' * 60}")
    print(f"DONE! {len(listings)} listings scraped")
    print(f"  With date_of_birth: {with_dob} ({100*with_dob/len(listings):.0f}%)")
    print(f"  With ready_to_leave: {with_rtl} ({100*with_rtl/len(listings):.0f}%)")
    print(f"  With price: {with_price} ({100*with_price/len(listings):.0f}%)")
    print(f"  KC Registered: {kc_reg} ({100*kc_reg/len(listings):.0f}%)")
    print(f"  Errors: {errors}")
    print(f"\nSaved to:")
    print(f"  {OUTPUT_DIR / 'gundogs_direct_data.csv'}")


if __name__ == "__main__":
    asyncio.run(main())
