#!/usr/bin/env python3
"""
Better puppy count extraction using titles, descriptions, and gender data.
"""

import pandas as pd
import re

df = pd.read_csv('output/facts/facts.csv', low_memory=False)

def extract_puppy_count(row):
    """
    Extract puppy count from multiple sources in priority order:
    1. Explicit total_available
    2. Males + females sum
    3. Parse title/description for "litter of X", "X pups", "X boys/girls", etc.
    4. Default to 1
    """
    
    # Priority 1: Explicit count (if not already suspicious)
    if pd.notna(row['total_available']) and row['total_available'] != '':
        try:
            count = int(float(str(row['total_available']).strip()))
            if 1 <= count <= 20:  # Realistic range
                return count, "explicit"
        except:
            pass
    
    # Priority 2: Males + females
    try:
        males = float(row['males_available']) if pd.notna(row['males_available']) else 0
        females = float(row['females_available']) if pd.notna(row['females_available']) else 0
        total = int(males + females)
        if total > 0 and total <= 20:
            return total, "gender"
    except:
        pass
    
    # Priority 3: Parse title and description
    text = ""
    if pd.notna(row['title']):
        text += str(row['title']).lower() + " "
    # Note: description not in facts.csv, could be in raw data
    
    # Pattern: "litter of X"
    m = re.search(r'litter\s+of\s+(\d+)', text)
    if m:
        count = int(m.group(1))
        if 1 <= count <= 20:
            return count, "litter_title"
    
    # Pattern: "X pups" or "X puppies"
    m = re.search(r'(\d+)\s+(?:pup|puppy|puppies)', text)
    if m:
        count = int(m.group(1))
        if 1 <= count <= 20:
            return count, "count_title"
    
    # Pattern: "X boys" or "X girls" - extract numbers and sum
    boys = re.findall(r'(\d+)\s+(?:boy|male)', text)
    girls = re.findall(r'(\d+)\s+(?:girl|female)', text)
    if boys or girls:
        b_count = int(boys[0]) if boys else 0
        g_count = int(girls[0]) if girls else 0
        total = b_count + g_count
        if 1 <= total <= 20:
            return total, "gender_title"
    
    # Pattern: "X available" (but avoid years)
    m = re.search(r'(\d+)\s+available', text)
    if m:
        count = int(m.group(1))
        if 1 <= count <= 20:  # Avoid years
            return count, "available_title"
    
    # Default
    return 1, "singleton"

print("="*90)
print("IMPROVED EXTRACTION - ALL PLATFORMS")
print("="*90)

platforms = ['pets4homes', 'freeads', 'gumtree', 'foreverpuppy', 'petify', 'puppies', 'preloved', 'kennel_club', 'champdogs']

totals = {}
for platform in platforms:
    pltf = df[df['platform'] == platform].copy()
    pltf_unique = pltf.drop_duplicates(subset=['breed', 'location', 'price'])
    
    counts = []
    sources = []
    for idx, row in pltf_unique.iterrows():
        count, source = extract_puppy_count(row)
        counts.append(count)
        sources.append(source)
    
    pltf_unique['puppy_count'] = counts
    pltf_unique['count_source'] = sources
    
    total_pups = sum(counts)
    avg = total_pups / len(pltf_unique) if len(pltf_unique) > 0 else 0
    singletons = (pd.Series(sources) == 'singleton').sum()
    
    totals[platform] = {
        'listings': len(pltf_unique),
        'puppies': total_pups,
        'avg': avg,
        'singletons': singletons,
        'singleton_pct': 100 * singletons / len(pltf_unique) if len(pltf_unique) > 0 else 0,
    }
    
    print(f"\n{platform.upper():<20}")
    print(f"  Listings: {len(pltf_unique):,} | Puppies: {total_pups:,} | Avg: {avg:.2f}")
    print(f"  Singletons: {singletons:,} ({100*singletons/len(pltf_unique):.1f}%)")
    print(f"  Sources: {dict(pltf_unique['count_source'].value_counts())}")

print("\n" + "="*90)
print("IMPROVED SUMMARY TABLE")
print("="*90)
print(f"\n{'Platform':<20} {'Listings':>10} {'Puppies':>10} {'Avg/List':>10} {'Singletons %':>15}")
print("-"*90)

total_listings = 0
total_puppies = 0
for platform in platforms:
    info = totals[platform]
    print(f"{platform:<20} {info['listings']:>10,} {info['puppies']:>10,} {info['avg']:>10.2f} {info['singleton_pct']:>14.1f}%")
    total_listings += info['listings']
    total_puppies += info['puppies']

print("-"*90)
avg_total = total_puppies / total_listings if total_listings > 0 else 0
singleton_pct_total = 100 * sum(totals[p]['singletons'] for p in platforms) / total_listings
print(f"{'TOTAL':<20} {total_listings:>10,} {total_puppies:>10,} {avg_total:>10.2f} {singleton_pct_total:>14.1f}%")
print("="*90)

improvement = total_puppies - 48577
print(f"\nIMPROVEMENT: +{improvement:,} puppies ({100*improvement/48577:.1f}%)")
print(f"Singleton reduction: {singleton_pct_total:.1f}% (from 64%)")
