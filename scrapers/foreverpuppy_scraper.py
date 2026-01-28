#!/usr/bin/env python3
"""ForeverPuppy.co.uk - ALL ad types (For Sale, Stud, Wanted, Rehome)"""
import asyncio, json, csv, re
from datetime import datetime
from playwright.async_api import async_playwright

BASE = "https://www.foreverpuppy.co.uk"
URL = f"{BASE}/find-your-dog"

async def scrape():
    print(f"{'='*60}\nForeverPuppy Scraper (ALL TYPES)\nStarted: {datetime.now()}\n{'='*60}")
    all_listings = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            viewport={'width':1920,'height':1080}
        )
        page = await ctx.new_page()
        
        await page.goto(URL, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(2)
        html = await page.content()
        
        count = re.search(r'(\d+)\s+adverts', html)
        total = int(count.group(1)) if count else 0
        print(f"Total listings claimed: {total}")
        
        pages = max([int(m.group(1)) for m in re.finditer(r'page=(\d+)', html)] or [1])
        print(f"Pages to scrape: {pages}")
        
        for pg in range(1, pages + 1):
            url = URL if pg == 1 else f"{URL}?page={pg}"
            print(f"Page {pg}/{pages}...", end=" ", flush=True)
            
            await page.goto(url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(1)
            html = await page.content()
            
            # ALL ad types: for-sale, for-stud, wanted, rehome
            pattern = r'/(for-sale|for-stud|wanted|rehome)/([^/]+)/([^/]+)/(\d+)_([^"\'>\s]+)'
            matches = re.findall(pattern, html)
            seen = set()
            cnt = 0
            
            for ad_type, breed_slug, loc_slug, ad_id, slug in matches:
                if ad_id in seen: continue
                seen.add(ad_id)
                
                listing = {
                    'ad_id': ad_id,
                    'ad_type': ad_type.replace('-', ' ').title(),
                    'breed': breed_slug.replace('-', ' ').title(),
                    'location': loc_slug.replace('-', ' ').title() if loc_slug not in ['area','england'] else '',
                    'url': f"{BASE}/{ad_type}/{breed_slug}/{loc_slug}/{ad_id}_{slug}",
                    'title': '', 'price': '', 'age': '', 'ready_to_leave': '', 'available': '',
                    'microchipped': False, 'vaccinated': False, 'boys': False, 'girls': False
                }
                
                block_match = re.search(rf'{ad_id}[^<]*</a>.*?(?=\d{{12}}|$)', html, re.DOTALL)
                if block_match:
                    block = block_match.group(0)[:2000]
                    title = re.search(r'>([^<]{10,100})</a>', block)
                    if title: listing['title'] = title.group(1).strip()
                    price = re.search(r'£[\d,]+', block)
                    if price: listing['price'] = price.group(0)
                    listing['microchipped'] = 'icrochip' in block
                    listing['vaccinated'] = 'accination' in block
                    listing['boys'] = 'Boys' in block
                    listing['girls'] = 'Girls' in block
                
                all_listings.append(listing)
                cnt += 1
            
            print(f"{cnt} listings")
        
        await browser.close()
    
    seen = set()
    unique = [l for l in all_listings if l['ad_id'] not in seen and not seen.add(l['ad_id'])]
    
    print(f"\nTotal unique: {len(unique)}")
    
    # Count by type
    types = {}
    for l in unique:
        t = l.get('ad_type', 'Unknown')
        types[t] = types.get(t, 0) + 1
    print(f"By type: {types}")
    
    with open('foreverpuppy_FINAL.json', 'w') as f:
        json.dump(unique, f, indent=2)

    fields = ['ad_id','ad_type','title','price','breed','location','microchipped','vaccinated','boys','girls','url']
    with open('foreverpuppy_FINAL.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(unique)
    
    print(f"Saved: foreverpuppy_FINAL.csv & .json")
    prices = [int(l['price'].replace('£','').replace(',','')) for l in unique if l.get('price')]
    if prices: print(f"Price range: £{min(prices)} - £{max(prices)}, Avg: £{sum(prices)//len(prices)}")

if __name__ == '__main__':
    asyncio.run(scrape())
