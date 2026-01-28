#!/usr/bin/env python3
"""
PUPPIES.CO.UK - GOLDEN SCRAPER v2.1 (Playwright)
=================================================
Uses Playwright instead of undetected-chromedriver.

Usage:
    python3 puppies_golden_scraper.py
    python3 puppies_golden_scraper.py --resume
"""

from playwright.sync_api import sync_playwright
import json
import csv
import time
import random
import re
import os
import argparse
from datetime import datetime

class PuppiesGoldenScraper:
    def __init__(self):
        self.base_url = "https://www.puppies.co.uk"
        self.results = []
        self.seen_urls = set()
        self.browser = None
        self.page = None
        self.timestamp = datetime.now().strftime("%Y%m%d")
        
        self.csv_file = f"puppies_{self.timestamp}.csv"
        self.json_file = f"puppies_{self.timestamp}.json"
        self.urls_file = "puppies_urls_cache.json"
        self.progress_file = "puppies_progress.json"
        
        self.columns = [
            'url', 'title', 'breed', 'price', 'location', 'description',
            'seller_name', 'seller_type', 'posted_date', 'member_since', 'ad_reference',
            'kc_registered', 'microchipped', 'vaccinated', 'health_tested', 
            'vet_checked', 'wormed', 'flea_treated',
            'puppies_available', 'males_available', 'females_available',
            'ready_to_leave', 'date_of_birth', 'dam_info', 'sire_info', 'scrape_date'
        ]
    
    def start_browser(self, playwright):
        print("🚀 Starting browser...")
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        time.sleep(2)
    
    def close_browser(self):
        if self.browser:
            self.browser.close()
    
    def random_delay(self, min_sec=2, max_sec=4):
        time.sleep(random.uniform(min_sec, max_sec))
    
    def wait_for_cloudflare(self):
        content = self.page.content().lower()
        if "just a moment" in content:
            print("⏳", end=" ", flush=True)
            time.sleep(10)
            return "just a moment" not in self.page.content().lower()
        return True
    
    def collect_listing_urls(self, max_pages=100):
        print("\n" + "="*60)
        print("PHASE 1: COLLECTING LISTING URLs")
        print("="*60)
        
        listing_urls = []
        
        for page_num in range(1, max_pages + 1):
            url = f"{self.base_url}/sale" if page_num == 1 else f"{self.base_url}/sale?page={page_num}"
            print(f"  Page {page_num}...", end=" ", flush=True)
            
            try:
                self.page.goto(url, timeout=30000)
                self.random_delay(2, 4)
                
                if not self.wait_for_cloudflare():
                    print("✗ Cloudflare blocked")
                    continue
                
                links = self.page.query_selector_all("a[href*='/sale/']")
                
                new_count = 0
                for link in links:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    if '?' in href or 'page=' in href:
                        continue
                    
                    parts = [p for p in href.split('/') if p]
                    if len(parts) < 4:
                        continue
                    
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    if full_url not in self.seen_urls:
                        self.seen_urls.add(full_url)
                        listing_urls.append(full_url)
                        new_count += 1
                
                print(f"+{new_count} URLs (total: {len(listing_urls)})")
                
                if new_count == 0 and page_num > 3:
                    print("  No new URLs found, stopping pagination")
                    break
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        with open(self.urls_file, 'w') as f:
            json.dump(listing_urls, f, indent=2)
        
        print(f"\n✓ Found {len(listing_urls)} unique listing URLs")
        return listing_urls
    
    def extract_dates(self, desc_lower):
        ready = ''
        dob = ''
        
        ready_patterns = [
            r'ready[:\s]*to\s*(?:leave|go)[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'ready[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'ready[:\s]*(\d{1,2}(?:st|nd|rd|th)?\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s*\d{2,4})?)',
            r'ready\s+(\d{1,2}(?:st|nd|rd|th)?\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',
            r'leave[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'available[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
        ]
        
        for pattern in ready_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                ready = match.group(1).strip()
                break
        
        dob_patterns = [
            r'born[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'born[:\s]*(?:on\s*)?(\d{1,2}(?:st|nd|rd|th)?\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s*\d{2,4})?)',
            r'dob[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'date\s*of\s*birth[:\s]*([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})',
            r'born\s+(\d{1,2}(?:st|nd|rd|th)?\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                dob = match.group(1).strip()
                break
        
        return ready, dob
    
    def extract_availability(self, desc_lower):
        patterns = [
            r'(\d+)\s*(?:puppies?|pups?)\s*(?:available|left|remaining)',
            r'(?:only\s*)?(\d+)\s*(?:left|remaining|available)',
            r'litter\s*of\s*(\d+)',
            r'(\d+)\s*in\s*(?:the\s*)?litter',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                return match.group(1)
        
        return ''
    
    def extract_listing_data(self, url):
        data = {col: '' for col in self.columns}
        data['url'] = url
        data['scrape_date'] = datetime.now().isoformat()
        
        try:
            url_parts = url.split('/')
            if 'sale' in url_parts:
                idx = url_parts.index('sale')
                if idx + 1 < len(url_parts):
                    data['breed'] = url_parts[idx + 1].replace('-', ' ').title()
                if idx + 2 < len(url_parts):
                    data['location'] = url_parts[idx + 2].replace('-', ' ').title()
            
            html = self.page.content()
            
            # Title
            try:
                h1 = self.page.query_selector("h1")
                if h1:
                    data['title'] = h1.inner_text().strip()
            except:
                pass
            
            # Price
            price_match = re.search(r'£[\d,]+', html)
            if price_match:
                data['price'] = price_match.group(0)
            
            # Description
            for selector in ['[class*="description"]', '.listing-description', 'article', '.advert-description']:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        text = elem.inner_text().strip()
                        if len(text) > 50:
                            data['description'] = text[:2000]
                            break
                except:
                    pass
            
            desc_lower = data['description'].lower()
            
            # Seller info
            seller_elems = self.page.query_selector_all("[class*='seller']")
            for elem in seller_elems:
                try:
                    text = elem.inner_text().strip()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        line_lower = line.lower().strip()
                        
                        if i == 0 and not any(x in line_lower for x in ['posted', 'member', 'reference', 'breeder', 'hobby']):
                            if not data['seller_name'] and len(line.strip()) > 2:
                                data['seller_name'] = line.strip()
                        
                        if ('breeder' in line_lower or 'hobby' in line_lower) and not data['seller_type']:
                            data['seller_type'] = line.strip()
                        
                        if 'posted on:' in line_lower:
                            data['posted_date'] = line.split(':', 1)[-1].strip()
                        
                        if 'member since:' in line_lower:
                            data['member_since'] = line.split(':', 1)[-1].strip()
                        
                        if 'reference:' in line_lower:
                            data['ad_reference'] = line.split(':', 1)[-1].strip()
                except:
                    pass
            
            # Health fields (from description only)
            if re.search(r'\bkc\s*reg', desc_lower) or 'kennel club' in desc_lower:
                data['kc_registered'] = 'Yes'
            
            if 'microchip' in desc_lower:
                data['microchipped'] = 'Yes'
            
            if re.search(r'\bvaccin|\bjabs?\b|\binjection', desc_lower):
                data['vaccinated'] = 'Yes'
            
            if 'health test' in desc_lower or 'dna test' in desc_lower or 'tested clear' in desc_lower:
                data['health_tested'] = 'Yes'
            
            if 'vet check' in desc_lower or 'vet-check' in desc_lower:
                data['vet_checked'] = 'Yes'
            
            if re.search(r'\bworm', desc_lower):
                data['wormed'] = 'Yes'
            
            if 'flea' in desc_lower:
                data['flea_treated'] = 'Yes'
            
            # Dates
            data['ready_to_leave'], data['date_of_birth'] = self.extract_dates(desc_lower)
            
            # Availability
            data['puppies_available'] = self.extract_availability(desc_lower)
            
            males_match = re.search(r'(\d+)\s*(?:male|boy)', desc_lower)
            if males_match:
                data['males_available'] = males_match.group(1)
            
            females_match = re.search(r'(\d+)\s*(?:female|girl|bitch)', desc_lower)
            if females_match:
                data['females_available'] = females_match.group(1)
            
            # Parent info
            dam_match = re.search(r'(?:dam|mum|mother|mom)[:\s]+([^\n]{10,100})', desc_lower)
            if dam_match:
                data['dam_info'] = dam_match.group(1).strip()[:200]
            
            sire_match = re.search(r'(?:sire|dad|father)[:\s]+([^\n]{10,100})', desc_lower)
            if sire_match:
                data['sire_info'] = sire_match.group(1).strip()[:200]
            
            return data
            
        except Exception as e:
            print(f" [Extract error: {e}]", end="")
            return data
    
    def scrape_listings(self, listing_urls, start_from=0):
        print("\n" + "="*60)
        print("PHASE 2: SCRAPING INDIVIDUAL LISTINGS")
        print("="*60)
        
        total = len(listing_urls)
        
        for i, url in enumerate(listing_urls[start_from:], start_from + 1):
            slug = url.split('/')[-1][:40]
            print(f"  [{i}/{total}] {slug}...", end=" ", flush=True)
            
            try:
                self.page.goto(url, timeout=30000)
                self.random_delay(2, 3.5)
                
                if not self.wait_for_cloudflare():
                    print("✗ CF blocked")
                    continue
                
                data = self.extract_listing_data(url)
                
                if data.get('title') and 'moment' not in data.get('title', '').lower():
                    self.results.append(data)
                    seller = data.get('seller_name', '')[:15] or '?'
                    print(f"✓ {data.get('breed', '?')[:15]} | {seller}")
                else:
                    print("✗ expired/empty")
                
            except Exception as e:
                print(f"✗ {str(e)[:30]}")
            
            if i % 25 == 0:
                self.save_results()
                self.save_progress(i)
    
    def save_results(self):
        if not self.results:
            return
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"  💾 Saved {len(self.results)} listings")
    
    def save_progress(self, current_index):
        with open(self.progress_file, 'w') as f:
            json.dump({'last_index': current_index, 'timestamp': self.timestamp}, f)
    
    def load_progress(self):
        try:
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            
            with open(self.urls_file, 'r') as f:
                urls = json.load(f)
            
            json_files = [f for f in os.listdir('.') if f.startswith('puppies_') and f.endswith('.json') 
                          and 'urls' not in f and 'progress' not in f]
            if json_files:
                latest = sorted(json_files)[-1]
                with open(latest, 'r') as f:
                    self.results = json.load(f)
            
            return urls, progress.get('last_index', 0)
        except:
            return None, 0
    
    def print_summary(self):
        print("\n" + "="*60)
        print("SCRAPE COMPLETE - SUMMARY")
        print("="*60)
        print(f"Total listings: {len(self.results)}")
        
        if not self.results:
            return
        
        print("\nField fill rates:")
        key_fields = ['title', 'breed', 'price', 'location', 'seller_name', 'seller_type',
                      'kc_registered', 'microchipped', 'vaccinated', 'health_tested',
                      'puppies_available', 'date_of_birth', 'dam_info', 'sire_info']
        
        for field in key_fields:
            filled = sum(1 for d in self.results if d.get(field))
            pct = 100 * filled // len(self.results) if self.results else 0
            print(f"  {field}: {filled}/{len(self.results)} ({pct}%)")
        
        print("\nTop 10 breeds:")
        breeds = {}
        for item in self.results:
            b = item.get('breed', 'Unknown')
            breeds[b] = breeds.get(b, 0) + 1
        
        for breed, count in sorted(breeds.items(), key=lambda x: -x[1])[:10]:
            print(f"  {breed}: {count}")
        
        print(f"\nOutput files:")
        print(f"  {self.csv_file}")
        print(f"  {self.json_file}")
    
    def run(self, resume=False):
        print("="*60)
        print("🐕 PUPPIES.CO.UK GOLDEN SCRAPER v2.1 (Playwright)")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with sync_playwright() as playwright:
            try:
                self.start_browser(playwright)
                
                if resume:
                    urls, start_from = self.load_progress()
                    if urls:
                        print(f"\n📂 Resuming from listing #{start_from + 1}")
                        self.seen_urls = set(urls)
                    else:
                        print("\n⚠️ No previous run found, starting fresh")
                        urls = self.collect_listing_urls()
                        start_from = 0
                else:
                    urls = self.collect_listing_urls()
                    start_from = 0
                
                self.scrape_listings(urls, start_from)
                self.save_results()
                self.print_summary()
                
            finally:
                self.close_browser()
        
        print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Puppies.co.uk Golden Scraper v2.1')
    parser.add_argument('--resume', action='store_true', help='Resume from last run')
    args = parser.parse_args()
    
    scraper = PuppiesGoldenScraper()
    scraper.run(resume=args.resume)
