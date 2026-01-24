import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)

# Get unique listings
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

print("FREEADS ANALYSIS:")
freeads = df_unique[df_unique['platform'] == 'freeads'].copy()
freeads_with_total = freeads[freeads['total_available_num'].notna() & (freeads['total_available_num'] > 0)]
print(f"Total listings: {len(freeads):,}")
print(f"With total_available: {len(freeads_with_total):,}")
print(f"Total puppies claimed: {freeads_with_total['total_available_num'].sum():,.0f}")
print(f"Average per listing: {freeads_with_total['total_available_num'].mean():.1f}")
print(f"Max in single listing: {freeads_with_total['total_available_num'].max():.0f}")
print(f"Distribution:")
print(freeads_with_total['total_available_num'].describe())

print("\n" + "="*70)
print("\nPETS4HOMES ANALYSIS:")
p4h = df_unique[df_unique['platform'] == 'pets4homes'].copy()
p4h_with_total = p4h[p4h['total_available_num'].notna() & (p4h['total_available_num'] > 0)]
print(f"Total listings: {len(p4h):,}")
print(f"With total_available: {len(p4h_with_total):,}")
print(f"Total puppies claimed: {p4h_with_total['total_available_num'].sum():,.0f}")
print(f"Average per listing: {p4h_with_total['total_available_num'].mean():.1f}")
print(f"Max in single listing: {p4h_with_total['total_available_num'].max():.0f}")
print(f"Distribution:")
print(p4h_with_total['total_available_num'].describe())

print("\n" + "="*70)
print("\nFREEADS TOP LISTINGS (by puppies claimed):")
print(freeads_with_total.nlargest(10, 'total_available_num')[['breed', 'location', 'price_num', 'total_available_num', 'males_available_num', 'females_available_num', 'title']].to_string())

print("\n" + "="*70)
print("\nPETS4HOMES TOP LISTINGS (by puppies claimed):")
print(p4h_with_total.nlargest(10, 'total_available_num')[['breed', 'location', 'price_num', 'total_available_num', 'males_available_num', 'females_available_num', 'title']].to_string())
