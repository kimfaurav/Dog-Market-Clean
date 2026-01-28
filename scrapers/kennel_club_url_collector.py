from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv
import os

def scrape_page(driver):
    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div[class*='card']")
    
    for card in cards:
        try:
            text = card.text
            if not text or len(text) < 50 or 'Litter size' not in text:
                continue
            
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            data = {
                'breed': '',
                'location': '',
                'breeder_name': '',
                'litter_size': '',
                'born': '',
                'date_of_birth': '',
                'price': '',
                'sex': '',
                'colour': '',
                'about': '',
                'license_number': '',
                'council': '',
                'url': ''
            }
            
            if lines:
                data['breed'] = lines[0]
            if len(lines) > 1:
                data['location'] = lines[1]
            
            for i, line in enumerate(lines):
                if line == 'Litter size' and i+1 < len(lines):
                    litter_parts = []
                    for j in range(1, 3):
                        if i+j < len(lines) and ('Bitch' in lines[i+j] or 'Dog' in lines[i+j]):
                            litter_parts.append(lines[i+j])
                    data['litter_size'] = ', '.join(litter_parts)
                
                elif line == 'Born' and i+1 < len(lines):
                    data['born'] = lines[i+1]
                
                elif line == 'Date of birth' and i+1 < len(lines):
                    data['date_of_birth'] = lines[i+1]
                
                elif line == 'Price' and i+1 < len(lines):
                    data['price'] = lines[i+1]
                
                elif line == 'Sex' and i+1 < len(lines):
                    data['sex'] = lines[i+1]
                
                elif line == 'Colour' and i+1 < len(lines):
                    data['colour'] = lines[i+1]
                
                elif line == 'About this litter' and i+1 < len(lines):
                    data['about'] = lines[i+1]
                
                elif line == 'License number' and i+1 < len(lines):
                    data['license_number'] = lines[i+1]
                
                elif line == 'Council' and i+1 < len(lines):
                    data['council'] = lines[i+1]
                
                elif line.startswith('Mr ') or line.startswith('Mrs ') or line.startswith('Ms ') or line.startswith('Miss '):
                    data['breeder_name'] = line
            
            try:
                links = card.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    href = link.get_attribute('href')
                    if href and '/litter-adverts/' in href:
                        data['url'] = href
                        break
            except:
                pass
            
            if data['breed'] and data['url']:
                listings.append(data)
                    
        except:
            continue
    
    return listings

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

all_listings = []

try:
    base_url = 'https://www.royalkennelclub.com/search/find-a-puppy/?Breeds=&Distance=15&BreedStandardColours=False&MaleDogs=False&FemaleDogs=False&SireIsHealthTested=False&DamIsHealthTested=False&ParentsAreHealthTested=False&TotalResults=0&SortNearest=False&SearchRescueClubs=False&GeneralRescueClubs=False&pageNumber='
    
    print("🐕 KC Scraper - FULL ATTRIBUTES (Price, Sex, DOB)...\n")
    
    for page_num in range(1, 50):
        url = base_url + str(page_num)
        
        print(f"📄 Page {page_num}...")
        driver.get(url)
        
        if page_num == 1:
            time.sleep(5)
            try:
                cookie_btns = driver.find_elements(By.CSS_SELECTOR, 
                    "button[id*='accept'], button[class*='accept']")
                for btn in cookie_btns:
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                        break
                    except:
                        continue
            except:
                pass
        
        time.sleep(8)
        
        listings = scrape_page(driver)
        new_listings = [l for l in listings if not any(x['url'] == l['url'] for x in all_listings)]
        
        if new_listings:
            all_listings.extend(new_listings)
            print(f"   ✓ Found {len(new_listings)} new listings (total: {len(all_listings)})")
        else:
            print(f"   ✓ No new listings - stopping")
            break
    
    print(f"\n✅ TOTAL: {len(all_listings)} litter listings\n")
    
    if all_listings:
        os.makedirs('/Users/kimfaura/Desktop/Pets/KennelClub', exist_ok=True)
        with open('/Users/kimfaura/Desktop/Pets/KennelClub/kc_data.csv', 'w', newline='') as f:
            fieldnames = ['breed', 'location', 'breeder_name', 'litter_size', 'born', 
                         'date_of_birth', 'price', 'sex', 'colour', 'about', 
                         'license_number', 'council', 'url']
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(all_listings)
        
        print(f"💾 Saved to: /Users/kimfaura/Desktop/Pets/KennelClub/kc_data.csv\n")
        
        print(f"📊 Summary:")
        print(f"   Total listings: {len(all_listings)}")
        print(f"   With breeder names: {sum(1 for l in all_listings if l['breeder_name'])}")
        print(f"   With prices: {sum(1 for l in all_listings if l['price'])}")
        print(f"   With DOB: {sum(1 for l in all_listings if l['date_of_birth'])}")
        print(f"   With sex: {sum(1 for l in all_listings if l['sex'])}")
        print(f"   With license: {sum(1 for l in all_listings if l['license_number'])}")
        print(f"   Unique breeds: {len(set(l['breed'] for l in all_listings))}")
        
        print(f"\nSample listing:")
        sample = all_listings[0]
        for key, val in sample.items():
            if val:
                print(f"   {key}: {val[:50] if len(str(val)) > 50 else val}")
        
finally:
    driver.quit()
