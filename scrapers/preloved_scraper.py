#!/usr/bin/env python3
"""
PRELOVED DOG SCRAPER - PRODUCTION v2
Verified patterns - 15/15 fields tested working
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv, time, random, re

# === CONFIG ===
SEARCHES = ['puppy', 'puppies for sale', 'dog for sale', 'french bulldog', 
            'labrador', 'cockapoo', 'spaniel', 'german shepherd', 'bulldog',
            'dachshund', 'poodle', 'beagle', 'husky', 'collie', 'terrier',
            'golden retriever', 'rottweiler', 'shih tzu', 'chihuahua', 'pug']
MAX_PAGES_PER_SEARCH = 50
OUTPUT_FILE = 'preloved_data.csv'
ENRICHED_FILE = 'preloved_enriched.csv'

# === FILTERS ===
EXCLUDE_KEYWORDS = [
    'wanted', 'looking for', 'seeking', 'need a', 'rehome wanted',
    'coat', 'collar', 'lead', 'leash', 'bed', 'cage', 'crate', 'bowl', 'harness',
    'whelping box', 'training pad', 'pee pad', 'pen/gate', 'dog guard', 'kennel',
    'carrier', 'fence', 'stud service', 'walking', 'sitting', 'grooming', 'ultrasound',
    'figurine', 'ornament', 'statue', 'collectable', 'vintage', 'antique',
    'furreal', 'zhu zhu', 'toy', 'dvd', 'book set', 'jigsaw', 'puzzle',
    'cutting die', 'lladro', 'wade', 'ceramic', 'porcelain', 'china plate',
    'tin ', 'metal', 'imperial', 'slammer', 'shampoo', 'cologne', 'bob martin',
    'animology', 'groom professional', 'caravan', 'holiday park', 'static home',
    'motorhome', 'lodge', 'chalet', 'mobile home', 'volvo', 'vauxhall', 'citroen',
    'astra', 'berlingo', 'equestrian', 'land for sale', 'hayling island',
    'slush puppie', 'motorcycle', 'yamaha', 'honda', 'bicycle', 'guitar',
    'scooter', 'careco', 'hisense', 'washer', 'aibo', 'robot', 'incense burner',
    'foo dog', 'border fine art', 'mobility cart', 'python', 'snake', 'hatching', 'reptile',
    'lizard', 'gecko', 'tortoise', 'turtle', 'guinea pig', 'rabbit', 'hamster',
    'cat ', 'kitten', 'parrot', 'bird', 'fish'
]

# === BREED PATTERNS (280+) ===
BREED_PATTERNS = [
    (r'affenpinscher', 'Affenpinscher'),
    (r'afghan\s*hound', 'Afghan Hound'),
    (r'airedale', 'Airedale Terrier'),
    (r'japanese\s*akita', 'Japanese Akita Inu'),
    (r'akita', 'Akita'),
    (r'alapaha', 'Alapaha Blue Blood Bulldog'),
    (r'alaskan\s*malamute|malamute', 'Alaskan Malamute'),
    (r'american\s*bulldog', 'American Bulldog'),
    (r'american\s*bully', 'American Bully'),
    (r'american\s*cocker', 'American Cocker Spaniel'),
    (r'american\s*bull\s*staffy', 'American Bull Staffy'),
    (r'anatolian', 'Anatolian Shepherd'),
    (r'aussiedoodle', 'Aussiedoodle'),
    (r'australian\s*cattle', 'Australian Cattle Dog'),
    (r'australian\s*kelpie|kelpie', 'Australian Kelpie'),
    (r'australian\s*labradoodle', 'Australian Labradoodle'),
    (r'australian\s*shepherd|aussie\s*shepherd', 'Australian Shepherd'),
    (r'australian\s*silky', 'Australian Silky Terrier'),
    (r'australian\s*terrier', 'Australian Terrier'),
    (r'azawakh', 'Azawakh'),
    (r'bandog', 'Bandog'),
    (r'barbet', 'Barbet'),
    (r'basenji', 'Basenji'),
    (r'basset\s*bleu', 'Basset Bleu De Gascogne'),
    (r'basset\s*fauve', 'Basset Fauve de Bretagne'),
    (r'basset\s*hound|basset', 'Basset Hound'),
    (r'bavarian', 'Bavarian Mountain Hound'),
    (r'beaglier', 'Beaglier'),
    (r'beagle', 'Beagle'),
    (r'bearded\s*collie|beardie', 'Bearded Collie'),
    (r'beauceron', 'Beauceron'),
    (r'bedlington', 'Bedlington Terrier'),
    (r'belgian\s*shepherd|malinois|tervuren|groenendael', 'Belgian Shepherd Dog'),
    (r'bergamasco', 'Bergamasco'),
    (r'bernedoodle', 'Bernedoodle'),
    (r'bernese', 'Bernese Mountain Dog'),
    (r'bichon\s*frise|bichon', 'Bichon Frise'),
    (r'biewer', 'Biewer Terrier'),
    (r'russian\s*black\s*terrier|black\s*russian', 'Russian Black Terrier'),
    (r'bloodhound', 'Bloodhound'),
    (r'bocker', 'Bocker'),
    (r'boerboel', 'Boerboel'),
    (r'bolognese', 'Bolognese'),
    (r'borador', 'Borador'),
    (r'border\s*collie', 'Border Collie'),
    (r'border\s*terrier', 'Border Terrier'),
    (r'bordoodle', 'Bordoodle'),
    (r'borzoi', 'Borzoi'),
    (r'boston\s*terrier|boston', 'Boston Terrier'),
    (r'bouvier', 'Bouvier Des Flandres'),
    (r'boxer', 'Boxer'),
    (r'bracco\s*italiano|bracco', 'Bracco Italiano'),
    (r'briard', 'Briard'),
    (r'brittany\s*spaniel|brittany', 'Brittany Spaniel'),
    (r'miniature\s*bull\s*terrier', 'Miniature Bull Terrier'),
    (r'english\s*bull\s*terrier', 'English Bull Terrier'),
    (r'bull\s*terrier', 'Bull Terrier'),
    (r'english\s*bulldog', 'English Bulldog'),
    (r'bullmastiff', 'Bullmastiff'),
    (r'cairn\s*terrier|cairn', 'Cairn Terrier'),
    (r'canaan', 'Canaan Dog'),
    (r'canadian\s*eskimo', 'Canadian Eskimo Dog'),
    (r'cane\s*corso|corso', 'Cane Corso'),
    (r'cardigan\s*corgi|welsh\s*corgi\s*cardigan', 'Welsh Corgi Cardigan'),
    (r'catalan\s*sheepdog', 'Catalan Sheepdog'),
    (r'caucasian\s*shepherd|caucasian', 'Caucasian Shepherd Dog'),
    (r'cava\s*tzu|cavatzu', 'Cava Tzu'),
    (r'cavachon', 'Cavachon'),
    (r'cavalier\s*king\s*charles|cavalier|ckcs', 'Cavalier King Charles Spaniel'),
    (r'cavapoo|cavoodle', 'Cavapoo'),
    (r'cavapoochon', 'Cavapoochon'),
    (r'central\s*asian', 'Central Asian Shepherd'),
    (r'cesky\s*terrier', 'Cesky Terrier'),
    (r'chesapeake', 'Chesapeake Bay Retriever'),
    (r'chihuahua', 'Chihuahua'),
    (r'chinese\s*crested', 'Chinese Crested'),
    (r'chipoo', 'Chipoo'),
    (r'chiweenie', 'Chiweenie'),
    (r'chorkie', 'Chorkie'),
    (r'chow\s*chow|chow', 'Chow Chow'),
    (r'chug', 'Chug'),
    (r'clumber', 'Clumber Spaniel'),
    (r'cockalier', 'Cockalier'),
    (r'cockapoo', 'Cockapoo'),
    (r'cocker\s*spaniel|cocker', 'Cocker Spaniel'),
    (r'cockerdor|cockador', 'Cockerdor'),
    (r'rough\s*collie', 'Rough Collie'),
    (r'smooth\s*collie', 'Smooth Collie'),
    (r'coonhound', 'Coonhound'),
    (r'coton\s*de\s*tulear|coton', 'Coton de Tulear'),
    (r'curly\s*coated\s*retriever', 'Curly Coated Retriever'),
    (r'miniature\s*dachshund|mini\s*dachshund', 'Miniature Dachshund'),
    (r'dachshund|daxie|sausage\s*dog|teckel', 'Dachshund'),
    (r'dalmatian', 'Dalmatian'),
    (r'dandie\s*dinmont', 'Dandie Dinmont Terrier'),
    (r'deerhound|scottish\s*deerhound', 'Deerhound'),
    (r'dobermann|doberman', 'Dobermann'),
    (r'dogue\s*de\s*bordeaux|french\s*mastiff', 'Dogue de Bordeaux'),
    (r'dorset\s*olde\s*tyme', 'Dorset Olde Tyme Bulldogge'),
    (r'double\s*doodle', 'Double Doodle'),
    (r'doxiepoo', 'Doxiepoo'),
    (r'foxhound', 'Foxhound'),
    (r'english\s*setter', 'English Setter'),
    (r'english\s*springer|springer\s*spaniel', 'English Springer Spaniel'),
    (r'english\s*toy\s*terrier', 'English Toy Terrier'),
    (r'entlebucher', 'Entlebucher Mountain Dog'),
    (r'estrela', 'Estrela Mountain Dog'),
    (r'eurasier', 'Eurasier'),
    (r'field\s*spaniel', 'Field Spaniel'),
    (r'finnish\s*lapphund', 'Finnish Lapphund'),
    (r'finnish\s*spitz', 'Finnish Spitz'),
    (r'flat\s*coated\s*retriever|flatcoat', 'Flat Coated Retriever'),
    (r'fox\s*terrier', 'Fox Terrier'),
    (r'french\s*bull\s*dog|frenchie|french\s*bulldog', 'French Bulldog'),
    (r'frug', 'Frug'),
    (r'german\s*longhaired\s*pointer', 'German Longhaired Pointer'),
    (r'german\s*pinscher', 'German Pinscher'),
    (r'german\s*shepherd|gsd|alsatian', 'German Shepherd'),
    (r'german\s*shorthaired\s*pointer|gsp', 'German Shorthaired Pointer'),
    (r'german\s*spitz', 'German Spitz'),
    (r'german\s*wirehaired\s*pointer|gwp', 'German Wirehaired Pointer'),
    (r'giant\s*schnauzer', 'Giant Schnauzer'),
    (r'glen\s*of\s*imaal', 'Glen of Imaal Terrier'),
    (r'goldador', 'Goldador'),
    (r'golden\s*retriever|goldie', 'Golden Retriever'),
    (r'golden\s*shepherd', 'Golden Shepherd'),
    (r'goldendoodle|groodle', 'Goldendoodle'),
    (r'gordon\s*setter', 'Gordon Setter'),
    (r'great\s*dane', 'Great Dane'),
    (r'greater\s*swiss', 'Greater Swiss Mountain Dog'),
    (r'greenland\s*dog', 'Greenland Dog'),
    (r'greyhound', 'Greyhound'),
    (r'griffon\s*bruxellois|brussels\s*griffon', 'Griffon Bruxellois'),
    (r'hamiltonstovare', 'Hamiltonstovare'),
    (r'harrier', 'Harrier'),
    (r'havanese', 'Havanese'),
    (r'havapoo', 'Havapoo'),
    (r'hovawart', 'Hovawart'),
    (r'huskita', 'Huskita'),
    (r'siberian\s*husky|husky', 'Siberian Husky'),
    (r'ibizan\s*hound|ibizan', 'Ibizan Hound'),
    (r'irish\s*doodle', 'Irish Doodle'),
    (r'irish\s*setter', 'Irish Setter'),
    (r'irish\s*terrier', 'Irish Terrier'),
    (r'irish\s*water\s*spaniel', 'Irish Water Spaniel'),
    (r'irish\s*wolfhound', 'Irish Wolfhound'),
    (r'italian\s*greyhound|iggy', 'Italian Greyhound'),
    (r'jack\s*chi|jackchi', 'Jack Chi'),
    (r'jack\s*russell|jrt', 'Jack Russell'),
    (r'jackapoo|jackadoodle', 'Jackapoo'),
    (r'jackshund', 'Jackshund'),
    (r'japanese\s*chin', 'Japanese Chin'),
    (r'japanese\s*spitz', 'Japanese Spitz'),
    (r'jug\b', 'Jug'),
    (r'kangal', 'Turkish Kangal'),
    (r'keeshond', 'Keeshond'),
    (r'kerry\s*blue', 'Kerry Blue Terrier'),
    (r'king\s*charles\s*spaniel', 'King Charles Spaniel'),
    (r'komondor', 'Komondor'),
    (r'kooikerhondje', 'Kooikerhondje'),
    (r'korean\s*jindo|jindo', 'Korean Jindo'),
    (r'kuvasz', 'Hungarian Kuvasz'),
    (r'labradoodle', 'Labradoodle'),
    (r'labrador\s*retriever|labrador|lab\b', 'Labrador Retriever'),
    (r'lagotto\s*romagnolo|lagotto', 'Lagotto Romagnolo'),
    (r'lakeland\s*terrier|lakeland', 'Lakeland Terrier'),
    (r'lancashire\s*heeler', 'Lancashire Heeler'),
    (r'large\s*munsterlander|munsterlander', 'Large Munsterlander'),
    (r'leonberger|leo\b', 'Leonberger'),
    (r'lhasa\s*apso|lhasa', 'Lhasa Apso'),
    (r'lhasapoo', 'Lhasapoo'),
    (r'lowchen', 'Lowchen'),
    (r'lurcher', 'Lurcher'),
    (r'malshi|mal-shi', 'Malshi'),
    (r'maltese', 'Maltese'),
    (r'maltipom', 'Maltipom'),
    (r'maltipoo', 'Maltipoo'),
    (r'manchester\s*terrier', 'Manchester Terrier'),
    (r'maremma', 'Maremma Sheepdog'),
    (r'mastiff', 'Mastiff'),
    (r'mi-ki|miki', 'Mi-Ki'),
    (r'mini\s*goldendoodle', 'Mini Goldendoodle'),
    (r'miniature\s*american\s*shepherd', 'Miniature American Shepherd'),
    (r'miniature\s*pinscher|min\s*pin', 'Miniature Pinscher'),
    (r'miniature\s*schnauzer|mini\s*schnauzer', 'Miniature Schnauzer'),
    (r'mixed\s*breed|crossbreed|cross\s*breed|mongrel', 'Mixed Breed'),
    (r'morkie', 'Morkie'),
    (r'neapolitan\s*mastiff|neo\s*mastiff', 'Neapolitan Mastiff'),
    (r'huntaway', 'Huntaway'),
    (r'newfypoo', 'Newfypoo'),
    (r'newfoundland|newfie', 'Newfoundland'),
    (r'norfolk\s*terrier', 'Norfolk Terrier'),
    (r'northern\s*inuit', 'Northern Inuit'),
    (r'norwegian\s*buhund', 'Norwegian Buhund'),
    (r'norwegian\s*elkhound|elkhound', 'Norwegian Elkhound'),
    (r'norwich\s*terrier', 'Norwich Terrier'),
    (r'nova\s*scotia|toller', 'Nova Scotia Duck Tolling Retriever'),
    (r'old\s*english\s*sheepdog|oes\b', 'Old English Sheepdog'),
    (r'old\s*tyme\s*bulldog', 'Old Tyme Bulldog'),
    (r'olde\s*english\s*bulldogge', 'Olde English Bulldogge'),
    (r'otterhound', 'Otterhound'),
    (r'papillon', 'Papillon'),
    (r'parson\s*russell|prt', 'Parson Russell'),
    (r'patterdale\s*terrier|patterdale', 'Patterdale Terrier'),
    (r'patterjack', 'Patterjack'),
    (r'pekingese|peke\b', 'Pekingese'),
    (r'pembroke\s*corgi|welsh\s*corgi\s*pembroke|corgi', 'Welsh Corgi Pembroke'),
    (r'pharaoh\s*hound', 'Pharaoh Hound'),
    (r'picardy\s*spaniel', 'Picardy Spaniel'),
    (r'plummer\s*terrier', 'Plummer Terrier'),
    (r'pointer', 'Pointer'),
    (r'polish\s*lowland', 'Polish Lowland Sheepdog'),
    (r'pomapoo', 'Pomapoo'),
    (r'pomchi', 'Pomchi'),
    (r'pomeranian|pom\b', 'Pomeranian'),
    (r'pomsky', 'Pomsky'),
    (r'poochon|bichpoo', 'Poochon'),
    (r'miniature\s*poodle|mini\s*poodle', 'Miniature Poodle'),
    (r'standard\s*poodle', 'Standard Poodle'),
    (r'toy\s*poodle', 'Toy Poodle'),
    (r'poodle', 'Poodle'),
    (r'portuguese\s*podengo|podengo', 'Portuguese Podengo'),
    (r'portuguese\s*water\s*dog|pwd', 'Portuguese Water Dog'),
    (r'presa\s*canario|presa', 'Presa Canario'),
    (r'pugapoo', 'Pugapoo'),
    (r'puggle', 'Puggle'),
    (r'pug', 'Pug'),
    (r'hungarian\s*puli|puli', 'Hungarian Puli'),
    (r'hungarian\s*pumi|pumi', 'Hungarian Pumi'),
    (r'pyrenean\s*mastiff', 'Pyrenean Mastiff'),
    (r'pyrenean\s*mountain|great\s*pyrenees', 'Pyrenean Mountain Dog'),
    (r'pyrenean\s*sheepdog', 'Pyrenean Sheepdog'),
    (r'rhodesian\s*ridgeback|ridgeback', 'Rhodesian Ridgeback'),
    (r'rottweiler|rottie', 'Rottweiler'),
    (r'russian\s*toy', 'Russian Toy Terrier'),
    (r'saarloos\s*wolfdog|saarloos', 'Saarloos Wolfdog'),
    (r'saluki', 'Saluki'),
    (r'samoyed|sammy', 'Samoyed'),
    (r'schipperke', 'Schipperke'),
    (r'schnoodle', 'Schnoodle'),
    (r'scottish\s*terrier|scottie', 'Scottish Terrier'),
    (r'sealyham\s*terrier|sealyham', 'Sealyham Terrier'),
    (r'shar\s*pei|sharpei', 'Shar Pei'),
    (r'sheepadoodle', 'Sheepadoodle'),
    (r'sheprador', 'Sheprador'),
    (r'shepsky', 'Shepsky'),
    (r'shetland\s*sheepdog|sheltie', 'Shetland Sheepdog'),
    (r'japanese\s*shiba|shiba\s*inu|shiba', 'Japanese Shiba Inu'),
    (r'shichon', 'Shichon'),
    (r'shih\s*tzu|shihtzu', 'Shih Tzu'),
    (r'shihpoo|shipoo', 'Shihpoo'),
    (r'shorkie', 'Shorkie'),
    (r'shorty\s*bull', 'Shorty Bull'),
    (r'skye\s*terrier', 'Skye Terrier'),
    (r'sloughi', 'Sloughi'),
    (r'soft\s*coated\s*wheaten|wheaten\s*terrier', 'Soft Coated Wheaten Terrier'),
    (r'spanish\s*water\s*dog', 'Spanish Water Dog'),
    (r'italian\s*spinone|spinone', 'Italian Spinone'),
    (r'sporting\s*lucas', 'Sporting Lucas Terrier'),
    (r'springador', 'Springador'),
    (r'sprocker', 'Sprocker'),
    (r'sprollie', 'Sprollie'),
    (r'sproodle', 'Sproodle'),
    (r'st\.?\s*bernard|saint\s*bernard', 'Saint Bernard'),
    (r'stabyhoun', 'Stabyhoun'),
    (r'staffordshire\s*bull\s*terrier|staffie|staffy|sbt', 'Staffordshire Bull Terrier'),
    (r'schnauzer', 'Schnauzer'),
    (r'sussex\s*spaniel', 'Sussex Spaniel'),
    (r'swedish\s*lapphund', 'Swedish Lapphund'),
    (r'swedish\s*vallhund|vallhund', 'Swedish Vallhund'),
    (r'thai\s*ridgeback', 'Thai Ridgeback'),
    (r'tibetan\s*mastiff', 'Tibetan Mastiff'),
    (r'tibetan\s*spaniel', 'Tibetan Spaniel'),
    (r'tibetan\s*terrier', 'Tibetan Terrier'),
    (r'utonagan', 'Utonagan'),
    (r'hungarian\s*vizsla|vizsla', 'Hungarian Vizsla'),
    (r'weimaraner', 'Weimaraner'),
    (r'welsh\s*collie', 'Welsh Collie'),
    (r'welsh\s*springer\s*spaniel|welsh\s*springer', 'Welsh Springer Spaniel'),
    (r'welsh\s*terrier', 'Welsh Terrier'),
    (r'west\s*highland\s*terrier|westie|wht', 'West Highland Terrier'),
    (r'westiepoo', 'Westiepoo'),
    (r'whippet', 'Whippet'),
    (r'white\s*swiss\s*shepherd', 'White Swiss Shepherd'),
    (r'mexican\s*hairless|xoloitzcuintli|xolo', 'Mexican Hairless'),
    (r'yorkiepoo|yorkipoo', 'Yorkiepoo'),
    (r'yorkshire\s*terrier|yorkie', 'Yorkshire Terrier'),
    (r'yochon', 'Yochon'),
    (r'zuchon', 'Zuchon'),
    (r'bull\s*dog|bulldog', 'Bulldog'),
    (r'collie', 'Collie'),
    (r'terrier', 'Terrier'),
    (r'spaniel', 'Spaniel'),
    (r'retriever', 'Retriever'),
    (r'shepherd', 'Shepherd'),
    (r'setter', 'Setter'),
    (r'doodle', 'Doodle Mix'),
]

def setup_driver():
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver

def is_valid_listing(title):
    title_lower = title.lower()
    return not any(kw in title_lower for kw in EXCLUDE_KEYWORDS)

def extract_breed_from_title(title):
    title_lower = title.lower()
    for pattern, breed_name in BREED_PATTERNS:
        if re.search(pattern, title_lower):
            return breed_name
    return ''

def clean_location(loc):
    return re.sub(r'This advert is located in and around\s*', '', loc, flags=re.IGNORECASE).strip().strip(',')

def scrape_page(driver, url):
    listings = []
    try:
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        containers = driver.find_elements(By.CSS_SELECTOR, 'li.search-result')
        for container in containers:
            try:
                link = container.find_element(By.CSS_SELECTOR, 'a[href*="/adverts/show/"]')
                href = link.get_attribute('href')
                if not href or '/adverts/show/' not in href:
                    continue
                title = ''
                try:
                    title = container.find_element(By.CSS_SELECTOR, 'h2').text.strip()
                except:
                    pass
                if not title or not is_valid_listing(title):
                    continue
                price = ''
                try:
                    price_elem = container.find_element(By.CSS_SELECTOR, '[class*="price"]')
                    match = re.search(r'£[\d,]+(?:\.\d{2})?', price_elem.text)
                    if match:
                        price = match.group()
                except:
                    pass
                location = ''
                try:
                    loc_elem = container.find_element(By.CSS_SELECTOR, '[class*="location"]')
                    location = clean_location(loc_elem.text.strip())
                except:
                    pass
                listings.append({'title': title, 'price': price, 'location': location, 'url': href.split('?')[0]})
            except:
                continue
    except Exception as e:
        print(f"    Error: {e}")
    return listings

def enrich_listing(driver, url):
    """VERIFIED PATTERNS - 15/15 tested working"""
    data = {
        'breed': '', 'sex': '', 'age': '', 'ready_to_leave': '', 
        'kc_registered': '', 'microchipped': '', 'neutered': '', 
        'vaccinations': '', 'health_checks': '',
        'seller_type': '', 'views': '', 'created': '',
        'seller_name': '', 'membership_level': '', 'member_since': ''
    }
    
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 3))
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # VERIFIED PATTERNS
        patterns = {
            'breed': r'Breed\n([^\n]+)',
            'sex': r'Sex ([A-Za-z]+ ?[A-Za-z]*)\n',
            'age': r'Current Age ([^\n]+)',
            'ready_to_leave': r'Ready to Leave ([^\n]+)',
            'kc_registered': r'Kennel Club Registered\n(Yes[^\n]*|No)',
            'microchipped': r'Microchipped\n(Yes|No)',
            'neutered': r'Neutered\n(Yes|No)',
            'vaccinations': r'Vaccinations ([^\n]+)',
            'health_checks': r'Health Checks ([^\n]+)',
            'seller_type': r'Seller Type\n([^\n]+)',
            'views': r'This advert has had\n(\d+)',
            'created': r'This advert was\n(\d+ \w+ ago)',
            'seller_name': r'Listed by:\n([^\n]+)',
            'membership_level': r'is a\n(Premium|Standard|Basic) member',
            'member_since': r'Joined\nPreloved in\n([A-Za-z]+ \d{4})',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()[:100]
            
    except:
        pass
    
    return data

def main():
    driver = setup_driver()
    all_listings = []
    seen_urls = set()
    
    print("=" * 60)
    print("PRELOVED DOG SCRAPER - PRODUCTION v2 (Verified)")
    print("=" * 60)
    
    # PHASE 1: Collect
    print("\n📋 PHASE 1: Collecting listings...")
    try:
        for search_term in SEARCHES:
            print(f"\n🔍 '{search_term}'")
            empty_count = 0
            for page in range(1, MAX_PAGES_PER_SEARCH + 1):
                url = f"https://www.preloved.co.uk/search?keyword={search_term.replace(' ', '+')}&page={page}"
                print(f"  Page {page}", end=" ")
                listings = scrape_page(driver, url)
                new = [l for l in listings if l['url'] not in seen_urls]
                for l in new:
                    seen_urls.add(l['url'])
                print(f"-> {len(new)} new (total: {len(all_listings) + len(new)})")
                if not new:
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    all_listings.extend(new)
                time.sleep(random.uniform(2, 3))
    except KeyboardInterrupt:
        print("\nInterrupted!")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'price', 'location', 'url'])
        writer.writeheader()
        writer.writerows(all_listings)
    print(f"\n✓ Saved {len(all_listings)} listings to {OUTPUT_FILE}")
    
    # PHASE 2: Enrich
    print(f"\n📋 PHASE 2: Enriching {len(all_listings)} listings...")
    enriched = []
    fieldnames = ['title', 'price', 'location', 'url', 'breed', 'sex', 'age', 
                  'ready_to_leave', 'kc_registered', 'microchipped', 'neutered',
                  'vaccinations', 'health_checks', 'seller_type', 'views', 
                  'created', 'seller_name', 'membership_level', 'member_since']
    
    try:
        for i, listing in enumerate(all_listings, 1):
            print(f"\r  {i}/{len(all_listings)}", end='', flush=True)
            details = enrich_listing(driver, listing['url'])
            if not details['breed']:
                details['breed'] = extract_breed_from_title(listing['title'])
            listing.update(details)
            enriched.append(listing)
            if i % 50 == 0:
                with open(ENRICHED_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(enriched)
            time.sleep(random.uniform(1, 2))
    except KeyboardInterrupt:
        print("\nInterrupted!")
    finally:
        driver.quit()
    
    # Final filter
    final = [r for r in enriched if r.get('breed') or 
             (r.get('price', '').replace('£','').replace(',','').replace('.','').isdigit() and 
              float(r.get('price', '0').replace('£','').replace(',','') or 0) >= 100)]
    
    with open(ENRICHED_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final)
    
    # Stats
    stats = {
        'breed': sum(1 for r in final if r.get('breed')),
        'seller_name': sum(1 for r in final if r.get('seller_name')),
        'views': sum(1 for r in final if r.get('views')),
        'kc_registered': sum(1 for r in final if r.get('kc_registered')),
        'microchipped': sum(1 for r in final if r.get('microchipped')),
        'member_since': sum(1 for r in final if r.get('member_since')),
    }
    
    print(f"\n\n{'='*60}")
    print(f"✓ COMPLETE: {len(final)} dog listings")
    print(f"{'='*60}")
    for field, count in stats.items():
        pct = 100*count//len(final) if final else 0
        print(f"  {field:18} {pct:3}% ({count}/{len(final)})")
    print(f"{'='*60}")
    print(f"✓ Saved to: {ENRICHED_FILE}")

if __name__ == '__main__':
    main()
