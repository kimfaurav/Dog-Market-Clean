#!/usr/bin/env python3
"""
Identify suspicious sellers using location + name to create unique IDs
"""

import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

# Create unique seller ID (name + location)
facts['seller_unique_id'] = facts['seller_name'].fillna('') + ' | ' + facts['location'].fillna('')
derived['seller_unique_id'] = derived['seller_name'].fillna('') + ' | ' + derived['location'].fillna('')

print("UNIQUE SELLERS ANALYSIS\n")
print("=" * 100)

# Get top sellers by unique ID
top_sellers = facts['seller_unique_id'].value_counts().head(30)

print(f"Total unique sellers (name + location): {facts['seller_unique_id'].nunique():,}\n")
print("Top 30 sellers by listing count:\n")

suspicious_multiplatform = []

for seller_id, count in top_sellers.items():
    if seller_id.strip() == '|' or count < 5:
        continue
    
    seller_data = facts[facts['seller_unique_id'] == seller_id]
    platforms = seller_data['platform'].value_counts()
    breeds = seller_data['breed'].value_counts()
    
    # Extract name and location
    parts = seller_id.split(' | ')
    seller_name = parts[0] if len(parts) > 0 else '?'
    location = parts[1] if len(parts) > 1 else '?'
    
    print(f"{seller_name.ljust(25)} | {location.ljust(20)} | {count:>3} listings")
    
    # Check for multi-platform same seller
    if len(platforms) > 2:
        print(f"  ⚠️  SUSPICIOUS: {len(platforms)} platforms: {list(platforms.index)}")
        suspicious_multiplatform.append({
            'name': seller_name,
            'location': location,
            'listings': count,
            'platforms': len(platforms),
            'platform_list': list(platforms.index)
        })
    
    # Show breed distribution
    print(f"  Top breed: {breeds.index[0]} ({breeds.iloc[0]}/{count})")

print("\n" + "=" * 100)
print(f"\nSUSPICIOUS SELLERS (same person across 3+ platforms):\n")

if suspicious_multiplatform:
    for seller in suspicious_multiplatform:
        print(f"{seller['name'].ljust(25)} | {seller['location'].ljust(20)} | {seller['listings']:>3} listings | {seller['platforms']} platforms")
        print(f"  Platforms: {', '.join(seller['platform_list'])}")
else:
    print("✓ NO suspicious multi-platform sellers found")

print("\n" + "=" * 100)
print(f"\nDATASET QUALITY:")
print(f"  • Total records: {len(facts):,}")
print(f"  • Total unique sellers (name + location): {facts['seller_unique_id'].nunique():,}")
print(f"  • Average listings per seller: {len(facts) / facts['seller_unique_id'].nunique():.1f}")

