#!/usr/bin/env python3
"""
Champdogs Litter Scraper - PRODUCTION VERSION
Note: Detail pages require login, so all data comes from listing cards
"""

from playwright.sync_api import sync_playwright
import csv
import time
import random
import re
import json
from datetime import datetime
from urllib.parse import urljoin
from collections import Counter

BASE_URL = "https://www.champdogs.co.uk"
OUTPUT_CSV = "champdogs_complete.csv"

FIELDNAMES = [
    'url', 'listing_id', 'breed', 'sire_name', 'dam_name',
    'location', 'date_born', 'health_tested', 'raw_card_text'
]

BREED_ENDINGS = [
    'Retriever', 'Spaniel', 'Terrier', 'Hound', 'Setter', 'Pointer', 
    'Collie', 'Poodle', 'Dachshund', 'Schnauzer', 'Shepherd', 'Sheepdog',
    'Bulldog', 'Mastiff', 'Ridgeback', 'Vizsla', 'Weimaraner', 'Boxer',
    'Rottweiler', 'Dobermann', 'Dalmatian', 'Beagle', 'Whippet', 'Greyhound',
    'Samoyed', 'Husky', 'Malamute', 'Akita', 'Newfoundland', 'Papillon',
    'Chihuahua', 'Pomeranian', 'Pug', 'Maltese', 'Havanese', 'Basenji',
    'Tzu', 'Apso', 'Frise', 'Dane', 'Chow', 'Pei', 'Corgi', 'Spitz'
]

UK_LOCATIONS = [
    'Yorkshire', 'Lancashire', 'Devon', 'Cornwall', 'Kent', 'Surrey', 'Sussex',
    'Essex', 'Norfolk', 'Suffolk', 'Dorset', 'Somerset', 'Wiltshire', 'Hampshire',
    'Berkshire', 'Buckinghamshire', 'Oxfordshire', 'Gloucestershire', 'Worcestershire',
    'Herefordshire', 'Shropshire', 'Staffordshire', 'Warwickshire', 'Northamptonshire',
    'Leicestershire', 'Nottinghamshire', 'Lincolnshire', 'Derbyshire', 'Cheshire',
    'Merseyside', 'Cumbria', 'Durham', 'Northumberland', 'Cambridgeshire',
    'Bedfordshire', 'Hertfordshire', 'Scotland', 'Wales', 'Northern Ireland',
    'Tayside', 'Fife', 'Aberdeenshire', 'Ayrshire', 'Lanarkshire', 'Lothian',
    'Mid Glamorgan', 'South Glamorgan', 'West Glamorgan', 'Gwent', 'Powys',
    'Clwyd', 'Dyfed', 'Conwy', 'Flintshire', 'London', 'Midlands'
]

def human_delay(min_sec=1.5, max_sec=3.5):
    time.sleep(random.uniform(min_sec, max_sec))

def extract_listing_id(url):
    match = re.search(r'/litter/(\d+)', url)
    return match.group(1) if match else url.rstrip('/').split('/')[-1]

def clean_breed(breed_text):
    if not breed_text:
        return None
    words = breed_text.split()
    clean_words = []
    for word in words:
        if word in ['Ft', 'Ch', 'Sh', 'Int', 'FTCH', 'SHCH', 'FT', 'CH', 'ShCh']:
            break
        if len(clean_words) > 1 and re.match(r'^[A-Z][a-z]+[A-Z]', word):
            break
        clean_words.append(word)
        if word in BREED_ENDINGS:
            break
    return ' '.join(clean_words) if clean_words else None

def parse_card_text(card_text, url):
    data = {
        'url': url,
        'listing_id': extract_listing_id(url),
        'raw_card_text': card_text[:500]
    }
    
    lines = [l.strip() for l in card_text.split('\n') if l.strip()]
    is_new_litter = any('*** New Litter ***' in line for line in lines)
    
    if is_new_litter:
        # Format: Breed, *** New Litter ***, Location, Date, Health
        if lines:
            data['breed'] = lines[0]
    else:
        # Format: "Breed SireName x DamName Location Date Health"
        x_match = re.search(r'\s+x\s+', card_text)
        if x_match:
            before_x = card_text[:x_match.start()]
            after_x = card_text[x_match.end():]
            
            words = before_x.split()
            breed_words = []
            sire_words = []
            found_breed_end = False
            
            for word in words:
                if not found_breed_end:
                    breed_words.append(word)
                    if word in BREED_ENDINGS:
                        found_breed_end = True
                else:
                    sire_words.append(word)
            
            if breed_words:
                data['breed'] = clean_breed(' '.join(breed_words))
            if sire_words:
                data['sire_name'] = ' '.join(sire_words)
            
            # Dam name
            dam_words = []
            for word in after_x.split():
                if word in UK_LOCATIONS or re.match(r'^\d{1,2}(?:st|nd|rd|th)?$', word):
                    break
                dam_words.append(word)
            if dam_words:
                data['dam_name'] = ' '.join(dam_words[:10])
    
    # Location
    for loc in UK_LOCATIONS:
        if re.search(r'\b' + re.escape(loc) + r'\b', card_text, re.I):
            data['location'] = loc
            break
    
    # Date born
    date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', card_text)
    if date_match:
        data['date_born'] = date_match.group(1)
    
    # Health status
    card_lower = card_text.lower()
    if 'parents fully health tested' in card_lower:
        data['health_tested'] = 'Parents Fully Health Tested'
    elif 'parents health tested' in card_lower:
        data['health_tested'] = 'Parents Health Tested'
    elif 'sire fully health tested' in card_lower and 'dam fully health tested' in card_lower:
        data['health_tested'] = 'Both Fully Health Tested'
    elif 'sire fully health tested' in card_lower:
        data['health_tested'] = 'Sire Fully Health Tested'
    elif 'dam fully health tested' in card_lower:
        data['health_tested'] = 'Dam Fully Health Tested'
    elif 'health tested' in card_lower:
        data['health_tested'] = 'Yes'
    
    # Final cleanup
    if data.get('breed'):
        data['breed'] = clean_breed(data['breed'])
    
    return data

def run_scraper():
    print("=" * 70)
    print("CHAMPDOGS LITTER SCRAPER - PRODUCTION")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Note: Detail pages require login - extracting from card text only")
    print("=" * 70)
    
    all_urls = set()
    all_listings = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='en-GB',
            timezone_id='Europe/London'
        )
        
        page = context.new_page()
        
        print("\nLoading all listings...")
        page.goto(f"{BASE_URL}/litter/new?start=all", wait_until='networkidle', timeout=60000)
        human_delay(3, 5)
        
        # Cookie consent
        for sel in ['#onetrust-accept-btn-handler', 'button[id*="accept"]', '.cookie-accept']:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    human_delay(1, 2)
                    break
            except:
                pass
        
        # Scroll to load all
        for pct in [0.25, 0.5, 0.75, 1.0]:
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {pct})")
            human_delay(0.5, 1)
        
        # Extract all listings from cards
        links = page.query_selector_all('a[href*="/litter/"]')
        
        for link in links:
            href = link.get_attribute('href')
            if href and re.search(r'/litter/\d+', href):
                full_url = urljoin(BASE_URL, href)
                if full_url not in all_urls:
                    all_urls.add(full_url)
                    try:
                        parent = link.evaluate_handle('el => el.closest("tr, li, article, div")')
                        if parent:
                            card_text = parent.as_element().inner_text()
                            card_data = parse_card_text(card_text, full_url)
                            all_listings.append(card_data)
                            breed = card_data.get('breed', '?')[:25]
                            loc = card_data.get('location', '')[:15]
                            print(f"  [{len(all_listings):3}] {breed:<25} | {loc}")
                    except:
                        all_listings.append({'url': full_url, 'listing_id': extract_listing_id(full_url)})
        
        browser.close()
    
    # Save
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_listings)
    
    print("\n" + "=" * 70)
    print("✓✓✓ COMPLETE ✓✓✓")
    print("=" * 70)
    print(f"Total: {len(all_listings)} listings")
    print(f"Saved: {OUTPUT_CSV}")
    
    # Stats
    breeds = [l.get('breed') for l in all_listings if l.get('breed')]
    locations = [l.get('location') for l in all_listings if l.get('location')]
    health = [l for l in all_listings if l.get('health_tested')]
    
    print(f"\nCoverage: Breed {len(breeds)}/{len(all_listings)} | Location {len(locations)}/{len(all_listings)} | Health {len(health)}/{len(all_listings)}")
    
    print("\nTop breeds:")
    for breed, count in Counter(breeds).most_common(10):
        print(f"  {breed}: {count}")

if __name__ == '__main__':
    run_scraper()
