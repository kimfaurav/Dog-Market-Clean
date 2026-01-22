import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)

print("="*80)
print("VALIDATION RESULTS: Suspicious Puppy Counts Flagged & Corrected")
print("="*80)

# Show flagged listings
flagged = df[df['total_available_flag'] != 'ok'].copy()

print(f"\nTotal flagged: {len(flagged)} listings\n")

print("By flag type:")
print(flagged['total_available_flag'].value_counts().to_string())

print(f"\n\nDETAILS OF FLAGGED LISTINGS:")
print("-" * 80)

for flag_type in flagged['total_available_flag'].unique():
    subset = flagged[flagged['total_available_flag'] == flag_type]
    print(f"\n{flag_type.upper()}: {len(subset)} listings")
    for idx, row in subset.iterrows():
        print(f"  {row['breed']} | {row['location']} | Price: £{row['price_num']:.0f}")
        print(f"    Title: {row['title'][:80]}...")
        print(f"    Action: total_available_num set to NULL (was corrupted)")

print("\n" + "="*80)
print("\nREVISED PUPPY COUNT ESTIMATE:")
print("-" * 80)

df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

puppy_counts = []
for idx, row in df_unique.iterrows():
    count = None
    
    # Use validated total_available
    if pd.notna(row['total_available_num']) and row['total_available_num'] > 0:
        count = int(row['total_available_num'])
    # Otherwise use males + females
    elif pd.notna(row['males_available_num']) and pd.notna(row['females_available_num']):
        m = int(row['males_available_num']) if row['males_available_num'] > 0 else 0
        f = int(row['females_available_num']) if row['females_available_num'] > 0 else 0
        if m + f > 0:
            count = m + f
    
    if count is None:
        count = 1  # Default singleton
    
    puppy_counts.append(count)

total_puppies = sum(puppy_counts)
avg_per_listing = total_puppies / len(df_unique)

print(f"Unique listings: {len(df_unique):,}")
print(f"Total puppies: {total_puppies:,}")
print(f"Average per listing: {avg_per_listing:.1f}")

print("\nBy platform:")
for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform]
    pltf_count = []
    for idx, row in pltf.iterrows():
        count = None
        if pd.notna(row['total_available_num']) and row['total_available_num'] > 0:
            count = int(row['total_available_num'])
        elif pd.notna(row['males_available_num']) and pd.notna(row['females_available_num']):
            m = int(row['males_available_num']) if row['males_available_num'] > 0 else 0
            f = int(row['females_available_num']) if row['females_available_num'] > 0 else 0
            if m + f > 0:
                count = m + f
        if count is None:
            count = 1
        pltf_count.append(count)
    
    pltf_total = sum(pltf_count)
    pltf_avg = pltf_total / len(pltf) if len(pltf) > 0 else 0
    print(f"  {platform:15} {len(pltf):>6,} listings | {pltf_total:>7,} puppies | avg {pltf_avg:.1f}")

print("\n" + "="*80)
print("CONFIDENCE LEVELS (after validation):")
print("-" * 80)
print("⭐⭐⭐⭐⭐ Pets4homes, ForeverPuppy - Explicit counts validated")
print("⭐⭐⭐⭐ Petify - Gender split validated")
print("⭐⭐⭐ Others - Conservative singleton assumption")
