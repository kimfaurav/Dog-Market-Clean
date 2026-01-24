import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print("="*100)
print("PUPPY COUNT CONFIDENCE LEVELS - ALL 9 PLATFORMS")
print("="*100)

platforms_ordered = [
    'pets4homes', 'freeads', 'gumtree', 'foreverpuppy', 'petify', 
    'puppies', 'preloved', 'kennel_club', 'champdogs'
]

data = []

for platform in platforms_ordered:
    pltf = df_unique[df_unique['platform'] == platform]
    
    # Data availability
    has_total = (pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)).sum()
    has_gender = ((pltf['males_available_num'].notna()) & (pltf['females_available_num'].notna())).sum()
    has_dob = pltf['date_of_birth_ts'].notna().sum()
    
    coverage_total = 100 * has_total / len(pltf) if len(pltf) > 0 else 0
    coverage_gender = 100 * has_gender / len(pltf) if len(pltf) > 0 else 0
    coverage_dob = 100 * has_dob / len(pltf) if len(pltf) > 0 else 0
    
    # Calculate puppies
    pltf_count = []
    for idx, row in pltf.iterrows():
        count = None
        source = None
        
        if pd.notna(row['total_available_num']) and row['total_available_num'] > 0:
            count = int(row['total_available_num'])
            source = "explicit"
        elif pd.notna(row['males_available_num']) and pd.notna(row['females_available_num']):
            m = int(row['males_available_num']) if row['males_available_num'] > 0 else 0
            f = int(row['females_available_num']) if row['females_available_num'] > 0 else 0
            if m + f > 0:
                count = m + f
                source = "gender"
        
        if count is None:
            count = 1
            source = "singleton"
        
        pltf_count.append((count, source))
    
    total_pups = sum([c[0] for c in pltf_count])
    avg_pups = total_pups / len(pltf) if len(pltf) > 0 else 0
    
    # Assign confidence
    if coverage_total >= 90:
        confidence = "⭐⭐⭐⭐⭐"
        reason = "Explicit counts, validated, high coverage"
    elif coverage_total >= 50:
        confidence = "⭐⭐⭐⭐"
        reason = "Good explicit count coverage with validation"
    elif coverage_gender >= 90:
        confidence = "⭐⭐⭐⭐"
        reason = "Gender split, high coverage"
    elif coverage_dob >= 80:
        confidence = "⭐⭐⭐"
        reason = "DOB available, use DOB+8wks estimate"
    elif coverage_total > 10 or coverage_gender > 10:
        confidence = "⭐⭐"
        reason = "Partial data, mixed sources"
    else:
        confidence = "⭐"
        reason = "No quantity data, singleton assumption"
    
    data.append({
        'Platform': platform,
        'Listings': len(pltf),
        'Puppies': total_pups,
        'Avg/List': f"{avg_pups:.1f}",
        'Explicit %': f"{coverage_total:.0f}%",
        'Gender %': f"{coverage_gender:.0f}%",
        'DOB %': f"{coverage_dob:.0f}%",
        'Confidence': confidence,
        'Reasoning': reason
    })

df_summary = pd.DataFrame(data)

# Print main table
for idx, row in df_summary.iterrows():
    print(f"\n{row['Platform'].upper():20} {row['Confidence']}")
    print(f"  Listings: {row['Listings']:,} | Puppies: {row['Puppies']:,} | Avg: {row['Avg/List']} per listing")
    print(f"  Data sources: {row['Explicit %']} explicit | {row['Gender %']} gender | {row['DOB %']} DOB")
    print(f"  → {row['Reasoning']}")

print("\n" + "="*100)
print("SUMMARY TABLE")
print("="*100)

summary_table = df_summary[['Platform', 'Listings', 'Puppies', 'Avg/List', 'Explicit %', 'Gender %', 'Confidence']]
print(summary_table.to_string(index=False))

print("\n" + "="*100)
print("KEY FINDINGS")
print("="*100)

high_conf = df_summary[df_summary['Confidence'].str.contains('⭐⭐⭐⭐')]
print(f"\nHIGH CONFIDENCE ({len(high_conf)} platforms):")
for idx, row in high_conf.iterrows():
    print(f"  • {row['Platform']:15} {row['Puppies']:,} puppies - {row['Reasoning']}")

med_conf = df_summary[df_summary['Confidence'] == '⭐⭐⭐']
print(f"\nMEDIUM CONFIDENCE ({len(med_conf)} platforms):")
for idx, row in med_conf.iterrows():
    print(f"  • {row['Platform']:15} {row['Puppies']:,} puppies - {row['Reasoning']}")

low_conf = df_summary[df_summary['Confidence'].str.contains('⭐$')]
print(f"\nLOW CONFIDENCE ({len(low_conf)} platforms):")
for idx, row in low_conf.iterrows():
    print(f"  • {row['Platform']:15} {row['Puppies']:,} puppies - {row['Reasoning']}")

total_high = high_conf['Puppies'].sum()
total_med = med_conf['Puppies'].sum()
total_low = low_conf['Puppies'].sum()
total_all = df_summary['Puppies'].sum()

print(f"\n\nPUPPY DISTRIBUTION BY CONFIDENCE:")
print(f"  High confidence: {total_high:,} ({100*total_high/total_all:.1f}%)")
print(f"  Medium confidence: {total_med:,} ({100*total_med/total_all:.1f}%)")
print(f"  Low confidence: {total_low:,} ({100*total_low/total_all:.1f}%)")
print(f"  TOTAL: {total_all:,}")
