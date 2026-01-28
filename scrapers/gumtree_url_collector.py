from playwright.sync_api import sync_playwright
import time
import re
import json

BREED_SLUGS = [
    'afghan-hound', 'affenpinscher', 'akita', 'japanese-akita-inu', 'bearded-collie',
    'airedale-terrier', 'alapaha-blue-blood-bulldog', 'beauceron', 'american-bulldog',
    'alaskan-malamute', 'bedlington-terrier', 'belgian-shepherd-dog', 'american-bully',
    'american-cocker-spaniel', 'bernedoodle', 'bergamasco', 'anatolian-shepherd-dog',
    'bernese-mountain-dog', 'brittany-spaniel', 'australian-kelpie', 'bichon-frise',
    'bull-terrier', 'australian-labradoodle', 'entlebucher-mountain-dog', 'biewer-terrier',
    'english-bull-terrier', 'australian-shepherd', 'estrela-mountain-dog', 'bullmastiff',
    'english-bulldog', 'russian-black-terrier', 'australian-silky-terrier', 'australian-terrier',
    'eurasier', 'field-spaniel', 'cairn-terrier', 'bloodhound', 'azawakh', 'finnish-lapphund',
    'caledonian-wolfalike', 'bocker', 'barbet', 'finnish-spitz', 'canaan-dog', 'bolognese',
    'boerboel', 'canadian-eskimo-dog', 'flat-coated-retriever', 'basenji', 'chug', 'chow-chow',
    'fox-terrier', 'cane-corso', 'border-collie', 'border-terrier', 'basset-bleu-de-gascogne',
    'french-bulldog', 'welsh-corgi-cardigan', 'basset-fauve-de-bretagne', 'cirneco-dell-etna',
    'catalan-sheepdog', 'clumber-spaniel', 'bordoodle', 'basset-hound', 'frug', 'cockalier',
    'jagdterrier', 'caucasian-shepherd-dog', 'bavarian-mountain-hound', 'beagle', 'borzoi',
    'boston-terrier', 'cavachon', 'cockapoo', 'german-longhaired-pointer', 'beaglier',
    'bouvier-des-flandres', 'cavalier-king-charles-spaniel', 'german-pinscher', 'cocker-spaniel',
    'cavapoo', 'rough-collie', 'german-shepherd', 'german-shorthaired-pointer', 'boxer',
    'smooth-collie', 'bracco-italiano', 'cavapoochon', 'german-spitz', 'central-asian-shepherd',
    'braque-d-auvergne', 'coonhound', 'braque-du-bourbonnais', 'coton-de-tulear', 'cesky-terrier',
    'german-wirehaired-pointer', 'briard', 'chesapeake-bay-retriever', 'curly-coated-retriever',
    'giant-schnauzer', 'dachshund', 'chihuahua', 'glen-of-imaal-terrier', 'miniature-dachshund',
    'goldador', 'chinese-crested', 'dalmatian', 'chipoo', 'golden-retriever',
    'dandie-dinmont-terrier', 'chiweenie', 'goldendoodle', 'deerhound', 'chorkie',
    'basset-griffon-vendeen', 'grand-bleu-de-gascogne', 'dobermann', 'dogue-de-bordeaux',
    'great-dane', 'dorset-olde-tyme-bulldogge', 'double-doodle', 'english-setter', 'doxiepoo',
    'english-springer-spaniel', 'english-toy-terrier', 'greenland-dog',
    'greater-swiss-mountain-dog', 'greyhound', 'griffon-bruxellois', 'harrier', 'hamiltonstovare',
    'ibizan-hound', 'hovawart', 'irish-doodle', 'havanese', 'komondor', 'kooikerhondje',
    'irish-setter', 'irish-terrier', 'irish-water-spaniel', 'korean-jindo', 'irish-wolfhound',
    'kromfohrlander', 'hungarian-kuvasz', 'italian-greyhound', 'labradoodle', 'jack-russell',
    'labrador-retriever', 'large-munsterlander', 'lancashire-heeler', 'turkish-kangal', 'jug',
    'leonberger', 'keeshond', 'lhasa-apso', 'kerry-blue-terrier', 'king-charles-spaniel',
    'lhasapoo', 'kishu-dog', 'lowchen', 'malshi', 'lurcher', 'maltese', 'maltipoo',
    'manchester-terrier', 'mastiff', 'miniature-american-shepherd', 'mi-ki', 'miniature-pinscher',
    'miniature-schnauzer', 'mixed-breed', 'morkie', 'neapolitan-mastiff', 'newfoundland',
    'huntaway', 'norfolk-terrier', 'northern-inuit', 'norwegian-buhund', 'norwich-terrier',
    'saluki', 'nova-scotia-duck-tolling-retriever', 'norwegian-elkhound', 'polish-lowland-sheepdog',
    'old-english-sheepdog', 'samoyed', 'schipperke', 'old-tyme-bulldog', 'pomapoo', 'schnoodle',
    'olde-english-bulldogge', 'pomchi', 'scottish-terrier', 'otterhound', 'poochon',
    'parson-russell', 'segugio-italiano', 'patterdale-terrier', 'poodle', 'shar-pei',
    'patterjack', 'sheepadoodle', 'miniature-poodle', 'standard-poodle', 'shetland-sheepdog',
    'pekingese', 'toy-poodle', 'shepsky', 'welsh-corgi-pembroke', 'pharaoh-hound',
    'portuguese-podengo', 'shichon', 'japanese-shiba-inu', 'portuguese-sheepdog',
    'plummer-terrier', 'picardy-spaniel', 'portuguese-water-dog', 'shih-tzu', 'pointer',
    'shihpoo', 'presa-canario', 'pug', 'shorkie', 'puggle', 'shorty-bull', 'siberian-husky',
    'hungarian-puli', 'hungarian-pumi', 'skye-terrier', 'sloughi', 'pyrenean-mastiff',
    'pyrenean-mountain-dog', 'soft-coated-wheaten-terrier', 'spanish-water-dog',
    'pyrenean-sheepdog', 'rhodesian-ridgeback', 'italian-spinone', 'rottweiler',
    'sporting-lucas-terrier', 'russian-toy', 'saarloos-wolfdog', 'springador', 'sprocker',
    'sproodle', 'sprollie', 'saint-bernard', 'stabyhoun', 'staffordshire-bull-terrier',
    'sussex-spaniel', 'schnauzer', 'swedish-vallhund', 'thai-ridgeback', 'swedish-lapphund',
    'tibetan-spaniel', 'tibetan-mastiff', 'utonagan', 'tibetan-terrier', 'hungarian-vizsla',
    'weimaraner', 'welsh-collie', 'welsh-springer-spaniel', 'west-highland-terrier',
    'welsh-terrier', 'korthals-griffon', 'white-swiss-shepherd', 'yorkiepoo', 'whippet',
    'yorkshire-terrier', 'yochon', 'zuchon', 'jackapoo', 'lagotto-romagnolo', 'lakeland-terrier',
    'pomsky', 'pomeranian', 'sealyham-terrier', 'papillon'
]

def safe_goto(page, url, retries=3):
    for attempt in range(retries):
        try:
            page.goto(url, timeout=15000)
            return True
        except:
            if attempt < retries - 1:
                print(f'    Retry {attempt + 1}...')
                time.sleep(2)
    return False

def get_count_from_page(page):
    try:
        h1 = page.query_selector('h1')
        if h1:
            text = h1.inner_text()
            match = re.search(r'(\d+)\s*ads?\s*for', text)
            if match:
                return int(match.group(1))
    except:
        pass
    return 0

def collect_urls_from_page(page):
    urls = set()
    for i in range(5):
        page.evaluate(f'window.scrollTo(0, {1000 * (i + 1)})')
        time.sleep(0.3)
    
    links = page.query_selector_all('article a[href*="/p/dogs/"]')
    for link in links:
        href = link.get_attribute('href')
        if href:
            clean = href.split('?')[0]
            if clean.startswith('/'):
                clean = 'https://www.gumtree.com' + clean
            urls.add(clean)
    return urls

print('=' * 60)
print('GUMTREE ULTIMATE SCRAPER')
print('=' * 60)

all_urls = set()
breed_results = {}
total_expected = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    if not safe_goto(page, 'https://www.gumtree.com/pets/pets-for-sale/dogs'):
        print('Failed to load main page')
        exit(1)
    time.sleep(2)
    
    try:
        page.click('#onetrust-accept-btn-handler', timeout=3000)
    except:
        pass
    
    # Phase 1: Discover
    print('\n--- PHASE 1: DISCOVERING COUNTS ---')
    breeds_with_listings = []
    
    for i, breed in enumerate(BREED_SLUGS, 1):
        if safe_goto(page, f'https://www.gumtree.com/pets/pets-for-sale/dogs/{breed}'):
            time.sleep(0.5)
            count = get_count_from_page(page)
            if count > 0:
                breeds_with_listings.append((breed, count))
                total_expected += count
                print(f'  {i}/{len(BREED_SLUGS)} {breed}: {count}')
    
    print(f'\n✓ Found {len(breeds_with_listings)} breeds with {total_expected} total listings')
    breeds_with_listings.sort(key=lambda x: -x[1])
    
    # Phase 2: Collect
    print('\n--- PHASE 2: COLLECTING URLs ---')
    
    for i, (breed, expected) in enumerate(breeds_with_listings, 1):
        print(f'\n[{i}/{len(breeds_with_listings)}] {breed.upper()} (expect {expected})')
        
        if not safe_goto(page, f'https://www.gumtree.com/pets/pets-for-sale/dogs/{breed}'):
            continue
        time.sleep(2)
        
        breed_urls = set()
        page_num = 1
        
        while True:
            new_urls = collect_urls_from_page(page)
            before = len(breed_urls)
            breed_urls.update(new_urls)
            
            added = len(breed_urls) - before
            print(f'  Page {page_num}: +{added} (breed: {len(breed_urls)}/{expected})')
            
            if added == 0:
                break
            
            try:
                fwd = page.query_selector('[data-q="pagination-forward-page"]')
                if fwd and not fwd.get_attribute('disabled'):
                    fwd.click()
                    time.sleep(2)
                    page_num += 1
                else:
                    break
            except:
                break
        
        all_urls.update(breed_urls)
        
        pct = (len(breed_urls) / expected * 100) if expected > 0 else 0
        breed_results[breed] = {'got': len(breed_urls), 'expected': expected, 'pct': pct}
        
        status = '✓' if pct >= 80 else '⚠️'
        print(f'  {status} {len(breed_urls)}/{expected} ({pct:.0f}%) - Total: {len(all_urls)}')
        
        with open('gumtree_ULTIMATE_urls.txt', 'w') as f:
            f.write('\n'.join(sorted(all_urls)))
    
    browser.close()

print(f'\n{"="*60}')
print('COMPLETE!')
print(f'Expected: {total_expected}')
print(f'Unique URLs: {len(all_urls)}')
print(f'{"="*60}')

shortfalls = [(b, r['got'], r['expected'], r['pct']) 
              for b, r in breed_results.items() if r['pct'] < 80]

if shortfalls:
    print(f'\n⚠️ SHORTFALLS:')
    for breed, got, expected, pct in sorted(shortfalls, key=lambda x: x[3]):
        print(f'  {breed}: {got}/{expected} ({pct:.0f}%)')
else:
    print('\n✓ All breeds at 80%+ coverage!')

with open('gumtree_breed_results.json', 'w') as f:
    json.dump(breed_results, f, indent=2)

print(f'\n✓ Saved to gumtree_ULTIMATE_urls.txt')
