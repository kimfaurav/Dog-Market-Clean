import requests
from bs4 import BeautifulSoup
import json
import time
import random

def scrape_freeads(start_page=1, end_page=10):
    results = []
    
    # More realistic headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }
    
    session = requests.Session()
    
    for page_num in range(start_page, end_page + 1):
        url = f'https://www.freeads.co.uk/uk/buy-sell/pets/dogs/?page={page_num}'
        
        print(f"Scraping page {page_num}...")
        
        try:
            time.sleep(random.uniform(4, 7))
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"  Error: Status {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            listings = soup.find_all('article')
            
            page_count = 0
            for article in listings:
                title_elem = article.find('h2') or article.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                full_text = article.get_text(separator='|', strip=True)
                parts = [p.strip() for p in full_text.split('|') if p.strip()]
                
                price = next((p for p in parts if '£' in p), '')
                location = next((p for p in reversed(parts) if ',' in p and len(p) < 50), '')
                description = next((p[:200] for p in parts if len(p) > 50 and p != title), '')
                
                link = article.find('a')
                href = link.get('href', '') if link else ''
                full_url = f"https://www.freeads.co.uk{href}" if href and href.startswith('/') else href
                
                if title and full_url:
                    results.append({
                        'title': title,
                        'price': price,
                        'location': location,
                        'description': description,
                        'url': full_url
                    })
                    page_count += 1
            
            print(f"  Found {page_count} listings")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("Starting Freeads scrape...")
    data = scrape_freeads(1, 5)
    
    with open('freeads_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    if data:
        import csv
        with open('freeads_data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"\nComplete! Scraped {len(data)} listings")
        print("Saved to: freeads_data.json and freeads_data.csv")
    else:
        print("\nNo data found")
