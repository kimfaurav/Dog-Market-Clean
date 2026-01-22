import pandas as pd
import re

df = pd.read_csv('output/views/derived.csv', low_memory=False)

# Get unique listings (breed + location + price)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')
print(f"Analyzing {len(df_unique):,} unique listings\n")

# Method 1: Use total_available_num (explicit count)
has_total = df_unique['total_available_num'].notna() & (df_unique['total_available_num'] > 0)
total_from_total_available = df_unique[has_total]['total_available_num'].sum()
print(f"From total_available field: {has_total.sum():,} listings = {total_from_total_available:,.0f} puppies")

# Method 2: Use males + females where total_available is missing
no_total = df_unique['total_available_num'].isna() | (df_unique['total_available_num'] == 0)
has_males_females = no_total & df_unique['males_available_num'].notna() & df_unique['females_available_num'].notna()
total_from_split = (df_unique[has_males_females]['males_available_num'] + df_unique[has_males_females]['females_available_num']).sum()
print(f"From males+females: {has_males_females.sum():,} listings = {total_from_split:,.0f} puppies")

# Method 3: Parse title for "litter of X"
remaining = df_unique[no_total & ~has_males_females].copy()
litter_pattern = r'litter\s+of\s+(\d+)'
remaining['litter_from_title'] = remaining['title'].str.lower().str.extract(f'({litter_pattern})')[1].astype(float)

has_litter = remaining['litter_from_title'].notna()
total_from_title = remaining[has_litter]['litter_from_title'].sum()
print(f"From title 'litter of X': {has_litter.sum():,} listings = {total_from_title:,.0f} puppies")

# Method 4: Check if any number in title (e.g., "3 pups", "4 available")
no_litter = remaining[~has_litter].copy()
number_pattern = r'(\d+)\s*(?:pup|available|for|sale)'
no_litter['number_from_title'] = no_litter['title'].str.lower().str.extract(f'({number_pattern})')[1].astype(float)
has_number = no_litter['number_from_title'].notna()
total_from_numbers = no_litter[has_number]['number_from_title'].sum()
print(f"From title numbers: {has_number.sum():,} listings = {total_from_numbers:,.0f} puppies")

# Method 5: Default to 1 (single puppy listing)
default_singles = len(no_litter) - has_number.sum()
print(f"Default as singles: {default_singles:,} listings = {default_singles:,.0f} puppies")

# Total
grand_total = total_from_total_available + total_from_split + total_from_title + total_from_numbers + default_singles
avg_per_listing = grand_total / len(df_unique)

print(f"\n{'='*70}")
print(f"TOTAL PUPPIES: {grand_total:,.0f}")
print(f"Average per unique listing: {avg_per_listing:.1f}")
print(f"{'='*70}")

# Show distribution
print(f"\nBreakdown by method:")
print(f"  1. total_available: {100*total_from_total_available/grand_total:.1f}%")
print(f"  2. males+females: {100*total_from_split/grand_total:.1f}%")
print(f"  3. 'litter of X': {100*total_from_title/grand_total:.1f}%")
print(f"  4. title numbers: {100*total_from_numbers/grand_total:.1f}%")
print(f"  5. singleton assumed: {100*default_singles/grand_total:.1f}%")

# Show top platforms
print(f"\nBy platform (from total_available where present):")
for platform in df_unique['platform'].unique():
    pltf = df_unique[df_unique['platform'] == platform]
    pltf_total = pltf[pltf['total_available_num'].notna()]['total_available_num'].sum()
    pltf_count = (pltf['total_available_num'].notna()).sum()
    if pltf_total > 0:
        print(f"  {platform}: {pltf_total:,.0f} from {pltf_count:,} listings")
