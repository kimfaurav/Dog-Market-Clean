#!/usr/bin/env python3
"""
FreeAds Enrichment - COMPLETE VERSION
Extracts ALL 35 fields matching the successful Jan 15 dataset
"""

import asyncio
import csv
import re
import os
import json
import random
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
URLS_FILE = os.path.expanduser("~/Desktop/Pets/freeads_urls.txt")
OUTPUT_FILE = os.path.expanduser("~/Desktop/Pets/Freeads/freeads_enriched_COMPLETE.csv")
PROGRESS_FILE = os.path.expanduser("~/Desktop/Pets/Freeads/freeads_progress.json")
ERROR_LOG = os.path.expanduser("~/Desktop/Pets/Freeads/freeads_errors.log")

SAVE_EVERY = 50
MIN_DELAY = 1.5
MAX_DELAY = 3.0

# ALL 35 FIELDS from successful Jan 15 dataset
FIELDNAMES = [
    # Core listing info
    'url', 'ad_id', 'title', 'breed', 'price', 'location',
    'description', 'date_posted',
    
    # Puppy details
    'sex', 'color', 'age', 'puppy_age', 
    'litter_size', 'puppies_in_litter', 'ready_date',
    
    # Health & vaccinations
    'kc_registered', 'microchipped', 'vaccinated', 'wormed',
    'flea_treated', 'vet_checked', 'health_checked',
    
    # Parents & breeding
    'pedigree', 'dna_tested_parents', 'champion_bloodline',
    'mum_visible', 'dad_visible', 'parents_visible',
    
    # Extras
    'home_reared', 'family_reared', 'puppy_contract',
    'insurance', 'delivery_available',
    
    # Seller info
    'seller_name', 'image_urls',
    
    # Metadata
    'status', 'scraped_at'
]


# ============================================================
# PROVEN EXTRACTION METHODS
# ============================================================

def extract_breed_from_url(url):
    """PROVEN: Extract breed from URL path"""
    match = re.search(r'/dogs/([^/]+)/', url)
    if match:
        return match.group(1).replace('-', ' ').title()
    return ''


def extract_ad_id_from_url(url):
    """PROVEN: Extract ad ID from URL"""
    match = re.search(r'/(\d{7,})/', url)
    return match.group(1) if match else ''


def extract_location_from_title(title):
    """PROVEN: Extract location from title - 96.9% success rate"""
    if not title:
        return ''
    match = re.search(r' in ([A-Z][a-zA-Z\s\-\.\']+)$', title)
    if match:
        return match.group(1).strip()
    return ''


# ============================================================
# TEXT EXTRACTION HELPERS
# ============================================================

def check_yes_no(text, positive_patterns, check_description=True):
    """Check for Yes/No boolean fields in text"""
    text_lower = text.lower()
    
    for pattern in positive_patterns:
        if re.search(pattern, text_lower):
            # Check it's not negated
            negation = re.search(r'(not|no|won\'t|will not|cannot)\s*(?:be\s*)?' + pattern, text_lower)
            if not negation:
                return 'Yes'
    
    return ''


def extract_sex(text):
    """Extract sex/gender - handles various formats"""
    text_lower = text.lower()
    
    # Count males and females
    male_count = 0
    female_count = 0
    
    # "X boys/males"
    male_matches = re.findall(r'(\d+)\s*(?:boy|male)s?', text_lower)
    for m in male_matches:
        male_count += int(m)
    
    # "X girls/females"
    female_matches = re.findall(r'(\d+)\s*(?:girl|female)s?', text_lower)
    for m in female_matches:
        female_count += int(m)
    
    if male_count > 0 and female_count > 0:
        return f"{male_count} male, {female_count} female"
    elif male_count > 0:
        return f"Male" if male_count == 1 else f"Male ({male_count})"
    elif female_count > 0:
        return f"Female" if female_count == 1 else f"Female ({female_count})"
    
    # Single mentions
    if re.search(r'\b(boy|male)\b', text_lower) and not re.search(r'\b(girl|female)\b', text_lower):
        return "Male"
    elif re.search(r'\b(girl|female)\b', text_lower) and not re.search(r'\b(boy|male)\b', text_lower):
        return "Female"
    elif re.search(r'\b(boy|male)\b', text_lower) and re.search(r'\b(girl|female)\b', text_lower):
        return "Mixed"
    
    return ''


def extract_color(text):
    """Extract color from text"""
    text_lower = text.lower()
    
    # Common dog colors
    colors = [
        'black and tan', 'black & tan', 'blue and tan', 'blue & tan',
        'chocolate and tan', 'chocolate & tan', 'lilac and tan', 'lilac & tan',
        'red and white', 'black and white', 'brown and white',
        'tricolor', 'tri-color', 'tri color', 'merle', 'blue merle', 'red merle',
        'brindle', 'fawn', 'cream', 'white', 'black', 'chocolate', 'brown',
        'golden', 'red', 'apricot', 'silver', 'blue', 'lilac', 'champagne',
        'sable', 'wheaten', 'parti', 'piebald', 'harlequin', 'dapple'
    ]
    
    for color in colors:
        if color in text_lower:
            return color.title()
    
    # Try to find "colour: X" or "color: X"
    match = re.search(r'colou?r[:\s]+([a-zA-Z\s&]+?)(?:\.|,|$|\n)', text_lower)
    if match:
        return match.group(1).strip().title()
    
    return ''


def extract_age(text):
    """Extract age from text"""
    text_lower = text.lower()
    
    patterns = [
        r'(\d+)\s*weeks?\s*old',
        r'(\d+)\s*months?\s*old',
        r'(\d+)\s*years?\s*old',
        r'(\d+)\s*(?:and\s*a\s*half|\.5)\s*years?\s*old',
        r'(\d+)\s*weeks?(?:\s|,|\.)',
        r'(\d+)\s*months?(?:\s|,|\.)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            num = match.group(1)
            if 'year' in pattern:
                return f"{num} years"
            elif 'month' in pattern:
                return f"{num} months"
            else:
                return f"{num} weeks"
    
    return ''


def extract_litter_size(text):
    """Extract litter size"""
    text_lower = text.lower()
    
    patterns = [
        r'litter\s*(?:of|size)[:\s]*(\d+)',
        r'(\d+)\s*(?:in\s*(?:the\s*)?litter|puppies?\s*(?:in\s*)?litter)',
        r'(\d+)\s*(?:beautiful|gorgeous|lovely|stunning|healthy)?\s*(?:puppies|pups)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)
    
    return ''


def extract_puppies_available(text):
    """Extract number of puppies available"""
    text_lower = text.lower()
    
    patterns = [
        r'(\d+)\s*(?:puppies?|pups?)\s*(?:still\s*)?available',
        r'(\d+)\s*(?:left|remaining)',
        r'only\s*(\d+)\s*(?:left|remaining|available)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)
    
    return ''


def extract_ready_date(text):
    """Extract ready to leave date"""
    text_lower = text.lower()
    
    if 'ready now' in text_lower or 'ready to go' in text_lower or 'ready to leave now' in text_lower:
        return 'Now'
    
    # "ready on 3rd February"
    match = re.search(r'ready\s*(?:to\s*(?:leave|go))?\s*(?:on|from)?\s*(?:the\s*)?(\d{1,2}(?:st|nd|rd|th)?\s*(?:of\s*)?(?:january|february|march|april|may|june|july|august|september|october|november|december))', text_lower)
    if match:
        return match.group(1).title()
    
    # "ready at 8 weeks"
    match = re.search(r'ready\s*(?:to\s*(?:leave|go))?\s*(?:at|from)?\s*(\d+)\s*weeks?', text_lower)
    if match:
        return f"{match.group(1)} weeks"
    
    return ''


def extract_posted_date(text):
    """Extract posted date"""
    text_lower = text.lower()
    
    match = re.search(r'(\d+)\s*(minutes?|hours?|days?|weeks?|months?)\s*ago', text_lower)
    if match:
        return f"{match.group(1)} {match.group(2)} ago"
    
    return ''


# ============================================================
# MAIN EXTRACTION FUNCTION
# ============================================================

async def extract_listing_data(page, url):
    """Extract ALL fields from a FreeAds listing page"""
    data = {field: '' for field in FIELDNAMES}
    data['url'] = url
    data['ad_id'] = extract_ad_id_from_url(url)
    data['breed'] = extract_breed_from_url(url)
    data['scraped_at'] = datetime.now().isoformat()
    data['status'] = 'active'
    
    try:
        response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        if response and response.status == 404:
            data['status'] = 'removed'
            return data
        
        await page.wait_for_timeout(2000)
        content = await page.content()
        
        # Check if removed
        if 'has been removed' in content or 'no longer available' in content.lower():
            data['status'] = 'removed'
            return data
        
        # ========== TITLE ==========
        try:
            title_el = await page.query_selector('h1')
            if title_el:
                data['title'] = (await title_el.inner_text()).strip()
                data['location'] = extract_location_from_title(data['title'])
        except:
            pass
        
        # ========== PRICE ==========
        price_match = re.search(r'£[\d,]+', content)
        if price_match:
            data['price'] = price_match.group(0)
        
        # ========== DESCRIPTION ==========
        desc_selectors = [
            'span[itemprop="description"]',
            '.description',
            '[class*="description"]',
            '.ad-description',
            '.listing-content'
        ]
        for selector in desc_selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = (await el.inner_text()).strip()
                    if len(text) > 50 and 'Cookie' not in text and 'Accept' not in text:
                        data['description'] = text[:2000]
                        break
            except:
                continue
        
        # ========== SELLER NAME ==========
        seller_selectors = ['.seller-name', '.name.nowrap', '[class*="seller"] .name', '.advertiser-name']
        for selector in seller_selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    name = (await el.inner_text()).strip()
                    if name and len(name) < 50:
                        data['seller_name'] = name
                        break
            except:
                continue
        
        # ========== IMAGES ==========
        try:
            images = []
            img_elements = await page.query_selector_all('img')
            for img in img_elements:
                src = await img.get_attribute('src') or ''
                if 'freeads' in src and '/img/' in src and 'logo' not in src and 'icon' not in src:
                    if src not in images:
                        images.append(src)
            data['image_urls'] = '|'.join(images[:5])
        except:
            pass
        
        # ========== POSTED DATE ==========
        data['date_posted'] = extract_posted_date(content)
        
        # ========== EXTRACT FROM DESCRIPTION ==========
        full_text = f"{data['title']} {data['description']}"
        
        # Puppy details
        data['sex'] = extract_sex(full_text)
        data['color'] = extract_color(full_text)
        data['age'] = extract_age(full_text)
        data['puppy_age'] = data['age']  # Same field, different name
        data['litter_size'] = extract_litter_size(full_text)
        data['puppies_in_litter'] = extract_puppies_available(full_text) or data['litter_size']
        data['ready_date'] = extract_ready_date(full_text)
        
        # Health & vaccinations
        data['kc_registered'] = check_yes_no(full_text, [
            r'kc\s*reg', r'kennel\s*club', r'pedigree\s*papers', r'kc\s*papers'
        ])
        data['microchipped'] = check_yes_no(full_text, [
            r'microchip', r'micro-chip', r'will\s*be\s*chipped', r'\bchipped\b'
        ])
        data['vaccinated'] = check_yes_no(full_text, [
            r'vaccin', r'1st\s*jab', r'first\s*jab', r'first\s*injection', r'inocul'
        ])
        data['wormed'] = check_yes_no(full_text, [
            r'wormed', r'de-wormed', r'dewormed', r'worm\s*treat'
        ])
        data['flea_treated'] = check_yes_no(full_text, [
            r'flea\s*treat', r'flea-treat', r'deflea'
        ])
        data['vet_checked'] = check_yes_no(full_text, [
            r'vet\s*check', r'vet-check', r'veterinar'
        ])
        data['health_checked'] = check_yes_no(full_text, [
            r'health\s*check', r'health\s*test', r'health\s*screen'
        ])
        
        # Parents & breeding
        data['pedigree'] = check_yes_no(full_text, [
            r'pedigree', r'pure\s*bred', r'purebred'
        ])
        data['dna_tested_parents'] = check_yes_no(full_text, [
            r'dna\s*test', r'dna\s*clear', r'health\s*test.*parent', r'parent.*health\s*test'
        ])
        data['champion_bloodline'] = check_yes_no(full_text, [
            r'champion', r'show\s*line', r'show\s*quality'
        ])
        data['mum_visible'] = check_yes_no(full_text, [
            r'mum\s*can\s*be\s*seen', r'see\s*mum', r'view.*mum', r'mum.*view',
            r'mother\s*can\s*be\s*seen', r'dam\s*can\s*be\s*seen'
        ])
        data['dad_visible'] = check_yes_no(full_text, [
            r'dad\s*can\s*be\s*seen', r'see\s*dad', r'view.*dad', r'dad.*view',
            r'father\s*can\s*be\s*seen', r'sire\s*can\s*be\s*seen'
        ])
        data['parents_visible'] = check_yes_no(full_text, [
            r'both\s*parents', r'see\s*both', r'view\s*both', r'parents\s*can\s*be\s*seen'
        ])
        if data['mum_visible'] and data['dad_visible']:
            data['parents_visible'] = 'Yes'
        
        # Extras
        data['home_reared'] = check_yes_no(full_text, [
            r'home\s*rear', r'raised\s*in\s*(?:our|a|the)?\s*home', r'home\s*bred',
            r'raised\s*underfoot', r'raised\s*in.*house'
        ])
        data['family_reared'] = check_yes_no(full_text, [
            r'family\s*rear', r'raised\s*(?:in|with)\s*(?:our|a)?\s*family',
            r'family\s*home', r'family\s*pet'
        ])
        data['puppy_contract'] = check_yes_no(full_text, [
            r'puppy\s*contract', r'sales?\s*contract', r'contract\s*(?:will\s*be\s*)?provided'
        ])
        data['insurance'] = check_yes_no(full_text, [
            r'insurance', r'insured', r'weeks?\s*(?:free\s*)?insurance'
        ])
        data['delivery_available'] = check_yes_no(full_text, [
            r'deliver', r'can\s*(?:be\s*)?transport', r'transport\s*available',
            r'nationwide', r'uk\s*wide'
        ])
        
    except Exception as e:
        data['status'] = f'error: {str(e)[:50]}'
        with open(ERROR_LOG, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {url} | {str(e)}\n")
    
    return data


# ============================================================
# PROGRESS MANAGEMENT
# ============================================================

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': []}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


# ============================================================
# MAIN
# ============================================================

async def main():
    print("=" * 60)
    print("FreeAds COMPLETE Enrichment - ALL 35 Fields")
    print("=" * 60)
    
    if not os.path.exists(URLS_FILE):
        print(f"ERROR: {URLS_FILE} not found!")
        return
    
    with open(URLS_FILE, 'r') as f:
        all_urls = [line.strip() for line in f if line.strip()]
    
    print(f"Total URLs: {len(all_urls)}")
    
    progress = load_progress()
    completed_set = set(progress['completed'])
    
    urls_to_process = [url for url in all_urls if url not in completed_set]
    print(f"Already done: {len(completed_set)}")
    print(f"Remaining: {len(urls_to_process)}")
    
    if not urls_to_process:
        print("All done!")
        return
    
    write_header = not os.path.exists(OUTPUT_FILE)
    
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Fields: {len(FIELDNAMES)}")
    print("-" * 60)
    
    start_time = datetime.now()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        batch_results = []
        
        try:
            for i, url in enumerate(urls_to_process):
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    data = await extract_listing_data(page, url)
                    batch_results.append(data)
                    progress['completed'].append(url)
                    
                    total_done = len(progress['completed'])
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    rate = total_done / elapsed if elapsed > 0 else 0
                    eta = (len(all_urls) - total_done) / rate if rate > 0 else 0
                    
                    icon = "✓" if data['status'] == 'active' else "○"
                    title_short = data['title'][:35] if data['title'] else 'No title'
                    
                    print(f"{icon} [{total_done}/{len(all_urls)}] {title_short}... | {rate:.1f}/min | ETA: {eta:.0f}m")
                    
                except Exception as e:
                    progress['failed'].append(url)
                    print(f"✗ [{len(progress['completed'])}/{len(all_urls)}] Error: {str(e)[:40]}")
                
                finally:
                    await page.close()
                    await context.close()
                
                if len(batch_results) >= SAVE_EVERY:
                    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                        if write_header:
                            writer.writeheader()
                            write_header = False
                        writer.writerows(batch_results)
                    save_progress(progress)
                    batch_results = []
                    print(f"  💾 Saved ({len(progress['completed'])} total)")
                
                await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            if batch_results:
                with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    if write_header:
                        writer.writeheader()
                    writer.writerows(batch_results)
                save_progress(progress)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted! Saving...")
            if batch_results:
                with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    if write_header:
                        writer.writeheader()
                    writer.writerows(batch_results)
            save_progress(progress)
        
        finally:
            await browser.close()
    
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Processed: {len(progress['completed'])}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"Time: {elapsed:.1f} minutes")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
