#!/usr/bin/env python3
"""
Gumtree Enrichment Script - PERFECTED VERSION v3
Fixed: Uses SVG color (#028546 = green checkmark) to detect Yes/No badges
"""

from playwright.sync_api import sync_playwright
import json
import csv
import time
import random
import re
import sys
from pathlib import Path

DELAY_MIN = 2.0
DELAY_MAX = 4.0
SAVE_EVERY = 25

def human_delay(min_s=DELAY_MIN, max_s=DELAY_MAX):
    time.sleep(random.uniform(min_s, max_s))

def extract_from_json(content):
    """Extract data from embedded JSON"""
    data = {}
    patterns = {
        'breed': r'"dogBreed"\s*:\s*"([^"]*)"',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            data[key] = match.group(1)
    return data

def extract_listing(page, url):
    ad_id_match = re.search(r'/(\d{7,10})(?:["\s<]|$)', url)
    ad_id = ad_id_match.group(1) if ad_id_match else ''
    
    result = {'url': url, 'ad_id': ad_id}
    
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        human_delay(1, 2)
        page.wait_for_selector('h1', timeout=10000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(0.5)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)
        
        content = page.content()
        
        # Check for expired listing
        if 'ads in Dogs & Puppies' in content and 'itemprop="description"' not in content:
            result['error'] = 'Expired/redirected'
            return result
        
        # JSON extraction for breed
        json_data = extract_from_json(content)
        result.update(json_data)
        
        # Title
        try:
            el = page.query_selector('h1')
            if el: 
                title = el.inner_text().strip()
                if 'ads in Dogs' not in title:
                    result['title'] = title
        except: pass
        
        # Price
        try:
            for sel in ['[data-q="ad-price"]', '[class*="price"]']:
                el = page.query_selector(sel)
                if el:
                    price = el.inner_text().strip()
                    if '£' in price:
                        result['price'] = price
                        break
        except: pass
        
        # Location
        try:
            for sel in ['[data-q="ad-location"]', '[class*="location"]', '[itemprop="address"]']:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text and len(text) < 100:
                        result['location'] = text
                        break
        except: pass
        
        # Description
        try:
            for sel in ['[itemprop="description"]', '[data-q="ad-description"]']:
                el = page.query_selector(sel)
                if el:
                    result['description'] = ' '.join(el.inner_text().split()).strip()
                    break
        except: pass
        
        # Seller name
        try:
            for sel in ['[data-q="seller-name"]', '[class*="seller-name"]', '[class*="sellerName"]']:
                el = page.query_selector(sel)
                if el:
                    name = el.inner_text().strip()
                    if name.lower().startswith('contact '):
                        name = name[8:]
                    if name and len(name) < 50:
                        result['seller_name'] = name
                    break
        except: pass
        
        # Posted date
        try:
            posted_match = re.search(r'(\d+\s*(?:hours?|days?|weeks?|months?)\s*ago)', content, re.IGNORECASE)
            if posted_match:
                result['posted'] = posted_match.group(1)
        except: pass
        
        # =========================================================
        # BADGES - Use SVG color to detect Yes/No
        # Green (#028546) = Yes, Grey = No
        # =========================================================
        try:
            badges = page.query_selector_all('div[class*="e5d347f1"]')
            
            for badge in badges:
                html = badge.inner_html()
                text = badge.inner_text().strip()
                is_yes = '#028546' in html  # Green checkmark
                
                # Map badge text to field names
                if text == 'Deflead':
                    result['deflead'] = 'Yes' if is_yes else 'No'
                elif text == 'Microchipped':
                    result['microchipped'] = 'Yes' if is_yes else 'No'
                elif 'Neutered' in text or 'Spayed' in text:
                    result['neutered'] = 'Yes' if is_yes else 'No'
                elif text == 'Vaccinated':
                    result['vaccinated'] = 'Yes' if is_yes else 'No'
                elif 'Kennel Club' in text or 'KC' in text:
                    result['kc_registered'] = 'Yes' if is_yes else 'No'
                elif 'Health checked' in text:
                    result['health_checked'] = 'Yes' if is_yes else 'No'
                # Also extract breed, sex, age from badges
                elif text.startswith('Sex:'):
                    result['sex'] = text.replace('Sex:', '').strip()
                elif text.startswith('Age:'):
                    result['age_detail'] = text.replace('Age:', '').strip()
                elif text.startswith('Ready to leave:'):
                    result['ready_to_leave'] = text.replace('Ready to leave:', '').strip()
                elif not any(x in text for x in ['Sex', 'Age', 'Ready', 'Health', 'Deflead', 'Micro', 'Neuter', 'Vacci', 'Kennel', 'KC']):
                    # Likely the breed
                    if 'breed' not in result and len(text) > 2 and len(text) < 50:
                        result['breed'] = text
        except: pass
        
        # Ensure all fields exist
        for field in ['title', 'price', 'location', 'breed', 'sex', 'age_detail',
                      'ready_to_leave', 'microchipped', 'vaccinated', 'kc_registered', 
                      'health_checked', 'neutered', 'deflead', 'seller_name', 'posted', 'description']:
            if field not in result:
                result[field] = ''
        
        return result
    except Exception as e:
        result['error'] = str(e)[:100]
        return result

def main():
    url_file = sys.argv[1] if len(sys.argv) > 1 else 'gumtree_urls.txt'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'gumtree_final.json'
    
    with open(url_file, 'r') as f:
        all_urls = [line.strip() for line in f if line.strip().startswith('http')]
    print(f"Found {len(all_urls)} URLs")
    
    all_data = []
    processed_urls = set()
    if Path(output_file).exists():
        try:
            with open(output_file, 'r') as f:
                all_data = json.load(f)
            processed_urls = {d['url'] for d in all_data}
            print(f"Resuming: {len(processed_urls)} already done")
        except: pass
    
    urls_to_process = [u for u in all_urls if u not in processed_urls]
    print(f"Remaining: {len(urls_to_process)}")
    
    if not urls_to_process:
        print("All done!")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-GB', timezone_id='Europe/London'
        )
        page = context.new_page()
        
        page.goto('https://www.gumtree.com', timeout=30000)
        time.sleep(2)
        try:
            page.click('#onetrust-accept-btn-handler', timeout=5000)
            print("✓ Cookies accepted")
        except: pass
        human_delay(2, 3)
        
        for i, url in enumerate(urls_to_process, 1):
            total = len(processed_urls) + i
            print(f"[{total}/{len(all_urls)}] ", end='', flush=True)
            
            result = extract_listing(page, url)
            all_data.append(result)
            
            if result.get('seller_name') and result.get('breed'):
                print(f"✓ {result.get('breed', '')[:40]}")
            elif result.get('error'):
                print(f"✗ {result.get('error', '')[:40]}")
            else:
                print(f"? {url[-40:]}")
            
            if i % SAVE_EVERY == 0:
                with open(output_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                print(f"  >>> Saved ({len(all_data)})")
            human_delay()
        
        browser.close()
    
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    csv_file = output_file.replace('.json', '.csv')
    if all_data:
        fieldnames = ['url', 'ad_id', 'title', 'price', 'location', 'breed', 'sex', 
                      'age_detail', 'ready_to_leave', 'microchipped', 'vaccinated', 
                      'kc_registered', 'health_checked', 'neutered', 'deflead', 
                      'seller_name', 'posted', 'description', 'error']
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_data)
    
    print(f"\n✓ Done! {len(all_data)} listings")
    print(f"  Saved: {output_file}, {csv_file}")
    
    complete = [d for d in all_data if d.get('seller_name') and d.get('breed')]
    print(f"  Complete: {len(complete)}/{len(all_data)}")
    
    print("\nHealth indicators:")
    for field in ['microchipped', 'vaccinated', 'kc_registered', 'health_checked', 'neutered', 'deflead']:
        yes = len([d for d in complete if d.get(field) == 'Yes'])
        print(f"  {field:15}: {yes}/{len(complete)} ({100*yes/len(complete):.1f}%) Yes")

if __name__ == '__main__':
    main()
