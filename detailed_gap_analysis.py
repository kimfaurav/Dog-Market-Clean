import pandas as pd
from pathlib import Path

raw_dir = Path("Input/Raw CSVs")

# Exact raw column names
raw_columns = {
    "pets4homes": ["title", "breed", "date_of_birth", "males_available", "females_available", 
                   "total_available", "price", "description", "sellerBadges", "location", 
                   "ready_to_leave", "url", "created_at", "published_at", "refreshed_at", 
                   "views_count", "seller_id", "seller_name", "company_name", "user_type", 
                   "is_breeder", "active_listings", "active_pets", "member_since", "last_active", 
                   "response_hours", "license_num", "license_auth", "license_status", 
                   "license_valid", "kc_license", "email_verified", "phone_verified", 
                   "reviews", "rating"],
    "gumtree": ["url", "ad_id", "title", "price", "location", "breed", "sex", "age_detail", 
                "ready_to_leave", "microchipped", "vaccinated", "kc_registered", 
                "health_checked", "neutered", "deflead", "seller_name", "posted", "description"],
    "freeads": ["url", "ad_id", "title", "breed", "price", "location", "description", 
                "date_posted", "sex", "color", "age", "puppy_age", "litter_size", 
                "puppies_in_litter", "ready_date", "kc_registered", "microchipped", 
                "vaccinated", "wormed", "flea_treated", "vet_checked", "health_checked", 
                "pedigree", "dna_tested_parents", "champion_bloodline", "mum_visible", 
                "dad_visible", "parents_visible", "home_reared", "family_reared", 
                "puppy_contract", "insurance", "delivery_available", "seller_name", 
                "image_urls", "status", "scraped_at"],
    "preloved": ["title", "price", "location", "url", "breed", "sex", "age", "ready_to_leave", 
                 "kc_registered", "microchipped", "neutered", "vaccinations", "health_checks", 
                 "seller_type", "views", "created", "seller_name", "membership_level", 
                 "member_since"],
    "kennel_club": ["breed", "puppy_name", "location", "county", "litter_size", "born", 
                    "about", "price", "sex", "date_of_birth", "colour", "breeder_name", 
                    "phone", "sire", "dam", "sire_health_tested", "dam_health_tested", 
                    "parents_health_standard", "sire_in_stud_book", "license_number", 
                    "council", "url", "scraped_at"],
    "foreverpuppy": ["ad_id", "ad_type", "title", "price", "breed", "location", "age", 
                     "ready_to_leave", "litter_size", "available", "seller_name", 
                     "seller_type", "kc_registered", "microchipped", "vaccinated", 
                     "boys", "girls", "created", "reposted", "url"],
    "petify": ["id", "title", "breed", "price", "location", "males_available", 
               "females_available", "kc_registered", "microchipped", "vaccinated", 
               "seller_type", "id_verified", "member_since", "ready_to_leave", 
               "posted_ago", "views", "url", "scraped_at", "error"],
    "puppies": ["url", "title", "breed", "price", "location", "description", "seller_name", 
                "seller_type", "posted_date", "member_since", "ad_reference", "kc_registered", 
                "microchipped", "vaccinated", "health_tested", "vet_checked", "wormed", 
                "flea_treated", "puppies_available", "males_available", "females_available", 
                "ready_to_leave", "date_of_birth", "dam_info", "sire_info", "scrape_date"],
    "champdogs": ["url", "listing_id", "breed", "litter_name", "sire_name", "dam_name", 
                  "breeder_name", "breeder_url", "kennel_name", "location", "county", 
                  "date_born", "date_available", "puppies_available", "males_available", 
                  "females_available", "price", "kc_registered", "health_tested", 
                  "health_tests", "microchipped", "vaccinated", "wormed", "vet_checked", 
                  "five_star_breeder", "assured_breeder", "licensed_breeder", "description", 
                  "image_url", "raw_card_text"]
}

# What's in facts.csv (master schema)
facts = pd.read_csv('output/facts/facts.csv', nrows=0)
schema_fields = set(facts.columns.tolist()) - {'platform'}

print("VALUABLE FIELDS BEING LEFT BEHIND IN RAW DATA\n")
print("=" * 100)

# These are potentially valuable fields
valuable_unmapped = {
    "gumtree": ["sex", "age_detail", "microchipped", "vaccinated", "kc_registered", 
                "health_checked", "neutered", "deflead"],
    "freeads": ["sex", "color", "age", "puppy_age", "kc_registered", "microchipped", 
                "vaccinated", "wormed", "flea_treated", "vet_checked", "health_checked", 
                "pedigree", "dna_tested_parents", "champion_bloodline", "parents_visible", 
                "home_reared", "family_reared", "puppy_contract", "insurance"],
    "preloved": ["sex", "age", "kc_registered", "microchipped", "neutered", "vaccinations", 
                 "health_checks", "seller_type", "membership_level"],
    "kennel_club": ["sex", "colour", "phone", "sire", "dam", "sire_health_tested", 
                    "dam_health_tested"],
    "foreverpuppy": ["seller_type", "kc_registered", "microchipped", "vaccinated"],
    "petify": ["seller_type", "id_verified"],
    "puppies": ["seller_type", "health_tested", "vet_checked", "wormed", "flea_treated", 
                "dam_info", "sire_info"],
    "champdogs": ["sire_name", "dam_name", "kennel_name", "county", "health_tested", 
                  "health_tests", "five_star_breeder", "assured_breeder", "licensed_breeder"]
}

for platform in sorted(valuable_unmapped.keys()):
    unmapped = valuable_unmapped[platform]
    if unmapped:
        print(f"\n{platform.upper()} - {len(unmapped)} VALUABLE fields not extracted:")
        for field in unmapped:
            print(f"  ✗ {field}")

print("\n" + "=" * 100)
print("\nSUMMARY BY CATEGORY:\n")

# Group by what type of data is missing
categories = {
    "Health Info": ["microchipped", "vaccinated", "health_tested", "vet_checked", "wormed", 
                    "flea_treated", "health_checks", "pedigree", "dna_tested_parents"],
    "Breeding Info": ["sire", "dam", "sire_name", "dam_name", "sire_health_tested", 
                      "dam_health_tested", "champion_bloodline", "kennel_name", "litter_name"],
    "Seller/Breeder": ["seller_type", "phone", "breeder_url", "kennel_name", "id_verified",
                       "five_star_breeder", "assured_breeder", "licensed_breeder"],
    "Puppy Details": ["sex", "age", "age_detail", "color", "colour", "puppy_age"],
    "Availability": ["parents_visible", "mum_visible", "dad_visible", "home_reared", 
                     "family_reared", "delivery_available", "puppies_available", "available"],
    "Contract/Care": ["puppy_contract", "insurance"],
}

for category, fields in categories.items():
    available_in_raw = []
    for platform in valuable_unmapped.keys():
        for field in fields:
            if field in valuable_unmapped[platform]:
                if field not in available_in_raw:
                    available_in_raw.append(f"{field} ({platform})")
    
    if available_in_raw:
        print(f"{category}:")
        for item in available_in_raw[:5]:
            print(f"  • {item}")
        if len(available_in_raw) > 5:
            print(f"  ... and {len(available_in_raw) - 5} more")
        print()

print("=" * 100)
print("\nCONCLUSION:")
print("- Health/vaccination data: Available but not extracted")
print("- Breeding lineage: Sire/dam names available but not used")
print("- Seller credibility: Badges/status fields available")
print("- Puppy characteristics: Sex, colors, ages available but sparse")
