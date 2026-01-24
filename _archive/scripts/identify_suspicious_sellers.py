#!/usr/bin/env python3
import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', low_memory=False)

# Generic first names appearing across multiple platforms = likely fake sellers
suspicious = ['Sarah', 'Emma', 'Lisa', 'John', 'Michelle', 'Laura', 'Charlotte', 'Kelly', 'Amy', 'Chloe', 'Kirsty', 'Sam', 'Gemma', 'Louise']

print("SUSPICIOUS SELLERS ANALYSIS\n")
print("=" * 80)

total_suspicious = 0

for name in suspicious:
    data = facts[facts['seller_name'] == name]
    if len(data) == 0:
        continue
    total_suspicious += len(data)
    
    platforms = list(data['platform'].unique())
    num_platforms = len(platforms)
    
    print(f"\n'{name}' - {len(data)} listings ({num_platforms} platforms)")
    for plat in platforms:
        count = len(data[data['platform'] == plat])
        print(f"  • {plat}: {count}")

print(f"\n" + "=" * 80)
print(f"\nTOTAL: {total_suspicious} listings from suspicious sellers")
print(f"  = {total_suspicious/len(facts)*100:.1f}% of all {len(facts)} records")

print("\n" + "=" * 80)
print("\nPATTERN DETECTED:")
print("  ✗ Generic first names ONLY (Sarah, Emma, Lisa, John, etc.)")
print("  ✗ Appear across 4-6 different platforms SIMULTANEOUSLY")
print("  ✗ Selling wide variety of different breeds")
print("  ✗ Likely: Data scrapers/aggregators or resellers, NOT real breeders")

print("\n" + "=" * 80)
print("\nRECOMMENDATION:")
print("  Create 'seller_type' flag to identify and filter:")
print(f"  • Mark {len(suspicious)} names as 'AGGREGATOR/RESELLER'")
print(f"  • This affects {total_suspicious} listings")
print("  • EXCLUDE from 'breeder analysis'")
print("  • KEEP for 'platform/market analysis'")

print("\n" + "=" * 80)
print("\nADDITIONAL SUSPECT:")
print("\n'Pawprints2freedom' - 81 listings, 80/81 Mixed Breed, Preloved only")
print("  → Likely ANIMAL SHELTER/RESCUE (not a breeder)")
print("  → Mark as 'SHELTER'")
print("  → Exclude from breeder analysis")

print("\n" + "=" * 80)
