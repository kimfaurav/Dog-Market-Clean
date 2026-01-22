import pandas as pd
import re

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print("DERIVING PUPPY COUNTS FROM TITLES, DESCRIPTIONS, AND GENDER\n")
print("="*80)

for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform].copy()
    total_listings = len(pltf)
    
    puppy_counts = []
    
    for idx, row in pltf.iterrows():
        count = None
        source = None
        
        # Method 1: Explicit total_available
        if pd.notna(row['total_available_num']) and row['total_available_num'] > 0 and row['total_available_num'] <= 20:
            count = int(row['total_available_num'])
            source = "explicit"
        
        # Method 2: Males + Females
        elif pd.notna(row['males_available_num']) and pd.notna(row['females_available_num']):
            m = int(row['males_available_num']) if row['males_available_num'] > 0 else 0
            f = int(row['females_available_num']) if row['females_available_num'] > 0 else 0
            if m + f > 0:
                count = m + f
                source = "gender"
        
        # Method 3: Parse title for patterns
        if count is None and pd.notna(row['title']):
            title = str(row['title']).lower()
            
            # "litter of X"
            match = re.search(r'litter\s+of\s+(\d+)', title)
            if match:
                count = int(match.group(1))
                source = "litter_title"
            
            # "X puppies" or "X pups"
            if count is None:
                match = re.search(r'(\d+)\s+(?:puppy|puppies|pup|pups)', title)
                if match:
                    count = int(match.group(1))
                    source = "count_title"
            
            # "X available" or "X ready"
            if count is None:
                match = re.search(r'(\d+)\s+(?:available|ready)', title)
                if match:
                    count = int(match.group(1))
                    source = "available_title"
        
        # Method 4: Default to 1
        if count is None:
            count = 1
            source = "singleton"
        
        puppy_counts.append((count, source))
    
    pltf['puppy_count'] = [c[0] for c in puppy_counts]
    pltf['count_source'] = [c[1] for c in puppy_counts]
    
    # Summary
    total_puppies = pltf['puppy_count'].sum()
    avg_puppies = pltf['puppy_count'].mean()
    
    print(f"\n{platform.upper()}")
    print("-" * 80)
    print(f"Listings: {total_listings:,} | Total Puppies: {total_puppies:,} | Avg: {avg_puppies:.1f}")
    print(f"\nData sources:")
    for source in ['explicit', 'gender', 'litter_title', 'count_title', 'available_title', 'singleton']:
        count = (pltf['count_source'] == source).sum()
        pups = pltf[pltf['count_source'] == source]['puppy_count'].sum()
        if count > 0:
            print(f"  {source:20} {count:>6,} listings = {pups:>8,} puppies ({100*pups/total_puppies:>5.1f}%)")

print("\n" + "="*80)
print("\nGRAND TOTAL BY PLATFORM:")
print("-" * 80)

grand_data = []
for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform].copy()
    
    puppy_counts = []
    for idx, row in pltf.iterrows():
        count = None
        
        if pd.notna(row['total_available_num']) and row['total_available_num'] > 0 and row['total_available_num'] <= 20:
            count = int(row['total_available_num'])
        elif pd.notna(row['males_available_num']) and pd.notna(row['females_available_num']):
            m = int(row['males_available_num']) if row['males_available_num'] > 0 else 0
            f = int(row['females_available_num']) if row['females_available_num'] > 0 else 0
            if m + f > 0:
                count = m + f
        
        if count is None and pd.notna(row['title']):
            title = str(row['title']).lower()
            match = re.search(r'litter\s+of\s+(\d+)', title)
            if match:
                count = int(match.group(1))
            else:
                match = re.search(r'(\d+)\s+(?:puppy|puppies|pup|pups)', title)
                if match:
                    count = int(match.group(1))
        
        if count is None:
            count = 1
        
        puppy_counts.append(count)
    
    total_pups = sum(puppy_counts)
    avg = sum(puppy_counts) / len(puppy_counts) if puppy_counts else 0
    
    grand_data.append({
        'Platform': platform,
        'Listings': len(pltf),
        'Total Puppies': total_pups,
        'Avg/Listing': f"{avg:.1f}"
    })

grand_df = pd.DataFrame(grand_data)
print(grand_df.to_string(index=False))

total_all = grand_df['Total Puppies'].sum()
total_listings = grand_df['Listings'].sum()
print(f"\n{'='*80}")
print(f"GRAND TOTAL: {total_all:,} puppies across {total_listings:,} unique listings")
print(f"Average: {total_all/total_listings:.1f} puppies per listing")
