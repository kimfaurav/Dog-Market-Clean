import pandas as pd

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_clean = df.dropna(subset=['breed', 'location', 'price_num'])
combos = df_clean.groupby(['breed', 'location', 'price_num']).size()
multi = combos[combos > 1]

print(f"Total listings: {len(df):,}")
print(f"With breed+location+price: {len(df_clean):,}")
print(f"Unique combinations: {len(combos):,}")
print(f"Appearing 2+ times: {multi.sum():,} ({100*multi.sum()/len(df_clean):.1f}%)")
print(f"\nTop 10 duplicated:")
for (breed, loc, price), count in combos.nlargest(10).items():
    platforms = df_clean[(df_clean['breed']==breed) & (df_clean['location']==loc) & (df_clean['price_num']==price)]['platform'].unique()
    print(f"  {breed} | {loc} | £{price:.0f}: {count}x - {', '.join(platforms)}")
