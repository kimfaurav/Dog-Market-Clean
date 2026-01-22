import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)

# Get unique listings by breed+location+price
df_clean = df.dropna(subset=['breed', 'location', 'price_num'])
df_unique = df_clean.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print(f"Analyzing {len(df_unique):,} unique listings\n")

# Count puppies from structured fields
print("Availability field coverage:")
print(f"  total_available: {df_unique['total_available_num'].notna().sum():,} listings")
print(f"  males_available: {df_unique['males_available_num'].notna().sum():,} listings")
print(f"  females_available: {df_unique['females_available_num'].notna().sum():,} listings")

# Calculate total available
total_from_total = df_unique['total_available_num'].fillna(0).sum()
total_from_gender = (df_unique['males_available_num'].fillna(0) + df_unique['females_available_num'].fillna(0)).sum()

print(f"\nTotal puppies available:")
print(f"  From 'total_available': {total_from_total:,.0f}")
print(f"  From males+females: {total_from_gender:,.0f}")

# Use best available data
total_available = max(total_from_total, total_from_gender)

# Check for derived field
if 'total_available_num' in df_unique.columns:
    best_total = df_unique['total_available_num'].fillna(0).sum()
    if best_total == 0:
        best_total = total_from_gender
else:
    best_total = total_from_gender

print(f"\n{'='*60}")
print(f"BEST ESTIMATE: {best_total:,.0f} puppies available")
print(f"  Across {len(df_unique):,} unique listings")
print(f"  Average per listing: {best_total/len(df_unique):.1f}")
print(f"{'='*60}")

# Show distribution
print(f"\nDistribution by gender where specified:")
has_gender = df_unique[(df_unique['males_available_num'].notna()) | (df_unique['females_available_num'].notna())]
males_total = has_gender['males_available_num'].fillna(0).sum()
females_total = has_gender['females_available_num'].fillna(0).sum()
print(f"  Males: {males_total:,.0f}")
print(f"  Females: {females_total:,.0f}")
print(f"  Unknown: {best_total - males_total - females_total:,.0f}")

# Show by platform
print(f"\nBy platform:")
by_plat = df_unique.groupby('platform').agg({
    'total_available_num': 'sum',
    'url': 'count'
}).round(0)
by_plat.columns = ['puppies', 'listings']
by_plat['avg_per_listing'] = (by_plat['puppies'] / by_plat['listings']).round(1)
print(by_plat.astype(int))
