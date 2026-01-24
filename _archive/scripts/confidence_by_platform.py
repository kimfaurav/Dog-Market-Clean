import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print("PUPPY COUNT CONFIDENCE BY PLATFORM\n")
print("="*80)

for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform].copy()
    total_listings = len(pltf)
    
    # Check various data sources
    has_total = (pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)).sum()
    has_males = pltf['males_available_num'].notna().sum()
    has_females = pltf['females_available_num'].notna().sum()
    has_both = ((pltf['males_available_num'].notna()) & (pltf['females_available_num'].notna())).sum()
    
    # Quality checks
    with_total = pltf[pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)]
    outliers = (with_total['total_available_num'] > 20).sum()
    
    # Calculate coverage
    coverage_total = 100 * has_total / total_listings
    coverage_gender = 100 * has_both / total_listings
    
    # Average puppies per listing (realistic ones)
    realistic = with_total[with_total['total_available_num'] <= 20]
    if len(realistic) > 0:
        avg_puppies = realistic['total_available_num'].mean()
        median_puppies = realistic['total_available_num'].median()
    else:
        avg_puppies = median_puppies = 0
    
    print(f"\n{platform.upper()}")
    print("-" * 80)
    print(f"Total listings: {total_listings:,}")
    print(f"\nData Coverage:")
    print(f"  Total available: {has_total:,} listings ({coverage_total:.1f}%)")
    print(f"  Males/Females: {has_both:,} listings ({coverage_gender:.1f}%)")
    
    if has_total > 0:
        print(f"\nTotal Available Quality:")
        print(f"  Realistic (≤20): {len(realistic):,} listings")
        print(f"  Outliers (>20): {outliers} listings")
        if len(realistic) > 0:
            print(f"  Average: {avg_puppies:.1f} puppies/listing")
            print(f"  Median: {median_puppies:.0f} puppies/listing")
    
    # Confidence rating
    if coverage_total >= 80 and outliers == 0:
        confidence = "⭐⭐⭐⭐⭐ VERY HIGH"
    elif coverage_total >= 60 and outliers == 0:
        confidence = "⭐⭐⭐⭐ HIGH"
    elif coverage_total >= 40:
        if outliers == 0:
            confidence = "⭐⭐⭐ MEDIUM"
        else:
            confidence = "⭐⭐ MEDIUM-LOW"
    elif coverage_total >= 20:
        confidence = "⭐⭐ LOW"
    else:
        confidence = "⭐ VERY LOW"
    
    print(f"\nConfidence: {confidence}")

print("\n" + "="*80)
print("\nSUMMARY TABLE:")
print("-" * 80)

summary_data = []
for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform].copy()
    has_total = (pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)).sum()
    coverage = 100 * has_total / len(pltf)
    with_total = pltf[pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)]
    outliers = (with_total['total_available_num'] > 20).sum() if len(with_total) > 0 else 0
    
    summary_data.append({
        'Platform': platform,
        'Listings': len(pltf),
        'With Total': has_total,
        'Coverage %': f"{coverage:.0f}%",
        'Outliers': outliers,
        'Confidence': "⭐⭐⭐⭐⭐" if (coverage >= 80 and outliers == 0) else
                      "⭐⭐⭐⭐" if (coverage >= 60 and outliers == 0) else
                      "⭐⭐⭐" if (coverage >= 40 and outliers <= 5) else
                      "⭐⭐" if coverage >= 20 else "⭐"
    })

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n" + "="*80)
print("\nKEY TAKEAWAYS:")
print(f"HIGH confidence platforms: Pets4homes, ForeverPuppy (use directly)")
print(f"MEDIUM confidence platforms: Freeads (use with outlier filtering), Puppies (limited data)")
print(f"LOW confidence platforms: Others (assume 1 puppy per listing or use males/females)")
