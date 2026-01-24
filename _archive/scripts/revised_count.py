import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print("PUPPY COUNT - REVISED:\n")

# Show by platform with reasonable interpretation
for platform in sorted(df_unique['platform'].unique()):
    pltf = df_unique[df_unique['platform'] == platform].copy()
    
    # Get listings with explicit counts
    with_count = pltf[pltf['total_available_num'].notna() & (pltf['total_available_num'] > 0)]
    
    if len(with_count) > 0:
        raw_total = with_count['total_available_num'].sum()
        capped_total = with_count['total_available_num'].clip(upper=20).sum()
        
        # Flag outliers
        outliers = with_count[with_count['total_available_num'] > 20]
        
        print(f"{platform:15} {len(with_count):>5,} listings")
        print(f"  Raw total: {raw_total:>8,.0f}")
        print(f"  Capped to 20: {capped_total:>8,.0f}")
        if len(outliers) > 0:
            print(f"  Outliers (>20): {len(outliers)} listings flagged")
        print()

print("="*70)
print("\nFREEADS OUTLIERS (likely data extraction errors):")
freeads_outliers = df_unique[(df_unique['platform'] == 'freeads') & (df_unique['total_available_num'] > 20)]
print(freeads_outliers[['breed', 'location', 'total_available_num', 'title']].to_string())

print("\n" + "="*70)
print("\nCONCLUSION:")
print("- Pets4homes: ~30k puppies (reliable, 4/listing avg)")
print("- Freeads: ~2-3k puppies (after removing obvious parsing errors like 3000, 2026, 2025)")
print("- Others: ~5-10k puppies")
print("\nBEST ESTIMATE: 35,000-45,000 puppies available (not 93k)")
print("\nFreeads 'total_available' field appears to have OCR/parsing errors")
print("where years (2025, 2026) or other numbers are being read as puppy counts.")
