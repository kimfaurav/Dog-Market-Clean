#!/usr/bin/env python3

platforms_data = {
    'pets4homes': {'listings': 7280, 'puppies': 30006},
    'freeads': {'listings': 6071, 'puppies': 9431},
    'gumtree': {'listings': 1497, 'puppies': 1497},
    'foreverpuppy': {'listings': 604, 'puppies': 2404},
    'petify': {'listings': 575, 'puppies': 2817},
    'puppies': {'listings': 532, 'puppies': 1415},
    'preloved': {'listings': 571, 'puppies': 571},
    'kennel_club': {'listings': 392, 'puppies': 392},
    'champdogs': {'listings': 44, 'puppies': 44},
}

print("="*80)
print("CURRENT PUPPY COUNTS BY PLATFORM")
print("="*80)
print(f"\n{'Platform':<20} {'Listings':>10} {'Puppies':>10} {'Avg/Listing':>12} {'% Singletons':>15}")
print("-"*80)

total_listings = 0
total_puppies = 0

for platform in ['pets4homes', 'freeads', 'gumtree', 'foreverpuppy', 'petify', 'puppies', 'preloved', 'kennel_club', 'champdogs']:
    info = platforms_data[platform]
    listings = info['listings']
    puppies = info['puppies']
    avg = puppies / listings if listings > 0 else 0
    singleton_pct = 100 * (listings - (puppies - listings)) / listings if listings > 0 else 0
    
    print(f"{platform:<20} {listings:>10,} {puppies:>10,} {avg:>12.2f} {singleton_pct:>14.1f}%")
    total_listings += listings
    total_puppies += puppies

print("-"*80)
avg_total = total_puppies / total_listings if total_listings > 0 else 0
singleton_pct_total = 100 * (total_listings - (total_puppies - total_listings)) / total_listings
print(f"{'TOTAL':<20} {total_listings:>10,} {total_puppies:>10,} {avg_total:>12.2f} {singleton_pct_total:>14.1f}%")
print("="*80)

print("\nPLATFORMS DEFAULTING TO SINGLETONS:")
print("  Gumtree:     1,497 listings all 1 puppy (0% extraction)")
print("  Preloved:      571 listings all 1 puppy (0% extraction)")
print("  Kennel Club:   392 listings DOB+8wks fallback")
print("  Champdogs:      44 listings DOB+8wks fallback")
print("\nPOTENTIAL: Extract 2,068 more puppies from these low-confidence platforms")
