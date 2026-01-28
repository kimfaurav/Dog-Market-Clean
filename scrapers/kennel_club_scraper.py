from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv

def enrich_listing(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        
        text = driver.find_element(By.TAG_NAME, 'body').text
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        data = {
            'price': '',
            'sex': '',
            'date_of_birth': '',
            'colour': '',
            'breeder_name': '',
            'phone': '',
            'email': '',
            'county': '',
            'sire': '',
            'dam': '',
            'sire_health_tested': '',
            'dam_health_tested': '',
            'license_number': '',
            'council': ''
        }
        
        for i, line in enumerate(lines):
            if i+1 < len(lines):
                next_line = lines[i+1]
                
                if line == 'Price':
                    data['price'] = next_line
                elif line == 'Sex':
                    data['sex'] = next_line
                elif line == 'Date of birth':
                    data['date_of_birth'] = next_line
                elif line == 'Colour':
                    data['colour'] = next_line
                elif line == 'Name' and i > 0 and 'Breeder' in lines[i-1]:
                    data['breeder_name'] = next_line
                elif line == 'Phone':
                    data['phone'] = next_line
                elif line == 'EMAIL':
                    data['email'] = next_line
                elif line == 'County':
                    data['county'] = next_line
                elif line == 'Sire':
                    data['sire'] = next_line
                    # Check if health tested
                    if i+2 < len(lines) and 'Health Standard' in lines[i+2]:
                        data['sire_health_tested'] = 'Yes'
                elif line == 'Dam':
                    data['dam'] = next_line
                    if i+2 < len(lines) and 'Health Standard' in lines[i+2]:
                        data['dam_health_tested'] = 'Yes'
                elif 'License number' in line or 'Licence number' in line:
                    data['license_number'] = next_line
                elif line == 'Council':
                    data['council'] = next_line
        
        return data
        
    except Exception as e:
        print(f"   Error: {e}")
        return None

# Load existing data
with open('/Users/kimfaura/Desktop/Pets/KennelClub/kc_data.csv', 'r') as f:
    rows = list(csv.DictReader(f))

print(f"🐕 Full KC enrichment (Email, Sire, Dam)...\n")

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get('https://www.royalkennelclub.com')
    time.sleep(3)
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
    
    for i, row in enumerate(rows, 1):
        url = row.get('url', '')
        if not url:
            continue
        
        print(f"[{i}/{len(rows)}] {row['breed'][:30]}...")
        
        details = enrich_listing(driver, url)
        
        if details:
            row.update(details)
            extras = []
            if details['email']: extras.append(f"Email: ✓")
            if details['sire']: extras.append(f"Sire: ✓")
            if details['dam']: extras.append(f"Dam: ✓")
            if extras:
                print(f"   ✓ {' | '.join(extras)}")
        
        if i % 50 == 0:
            with open('/Users/kimfaura/Desktop/Pets/KennelClub/kc_data_full.csv', 'w', newline='') as f:
                fieldnames = list(rows[0].keys())
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            print(f"\n💾 Progress saved ({i}/{len(rows)})\n")
    
    with open('/Users/kimfaura/Desktop/Pets/KennelClub/kc_data_full.csv', 'w', newline='') as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    
    print(f"\n✅ Full enrichment complete!")
    print(f"   Total listings: {len(rows)}")
    print(f"   With breeder names: {sum(1 for r in rows if r.get('breeder_name'))}")
    print(f"   With phone: {sum(1 for r in rows if r.get('phone'))}")
    print(f"   With email: {sum(1 for r in rows if r.get('email'))}")
    print(f"   With sire: {sum(1 for r in rows if r.get('sire'))}")
    print(f"   With dam: {sum(1 for r in rows if r.get('dam'))}")
    print(f"   Sire health tested: {sum(1 for r in rows if r.get('sire_health_tested'))}")
    print(f"   Dam health tested: {sum(1 for r in rows if r.get('dam_health_tested'))}")
    print(f"   With prices: {sum(1 for r in rows if r.get('price'))}")
    print(f"\n💾 Saved to: /Users/kimfaura/Desktop/Pets/KennelClub/kc_data_full.csv")
    
finally:
    driver.quit()
