import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load the derived CSV with low_memory=False to handle mixed types properly
print("Loading derived.csv...")
df = pd.read_csv('/Users/kimfaura/Desktop/Dog_Market_Clean/output/views/derived.csv', low_memory=False)
print(f"✓ Loaded {len(df):,} rows\n")

# ==================== 1. DUPLICATE URLs ====================
print("=" * 80)
print("1. DUPLICATE URLS CHECK")
print("=" * 80)
duplicate_urls = df[df.duplicated(subset=['url'], keep=False)]
print(f"Total duplicate URL occurrences: {len(duplicate_urls)}")
if len(duplicate_urls) > 0:
    print("\nDuplicate URL examples:")
    print(duplicate_urls[['platform', 'url', 'created_at']].head(10))
else:
    print("✓ No duplicate URLs found")
print()

# ==================== 2. PRICE OUTLIERS ====================
print("=" * 80)
print("2. PRICE OUTLIERS (Under £50 or Over £10,000)")
print("=" * 80)
# Filter rows where price_num is not null
price_data = df[df['price_num'].notna()].copy()
print(f"Total rows with price data: {len(price_data):,}")

# Check for under £50
under_50 = price_data[price_data['price_num'] < 50]
print(f"\nPrices under £50: {len(under_50)}")
if len(under_50) > 0:
    print("\nExamples:")
    print(under_50[['platform', 'title', 'breed', 'price', 'price_num']].head(10))

# Check for over £10,000
over_10k = price_data[price_data['price_num'] > 10000]
print(f"\nPrices over £10,000: {len(over_10k)}")
if len(over_10k) > 0:
    print("\nExamples:")
    print(over_10k[['platform', 'title', 'breed', 'price', 'price_num']].head(10))

# Summary statistics
print(f"\nPrice Statistics (£):")
print(f"  Min: £{price_data['price_num'].min():.0f}")
print(f"  Max: £{price_data['price_num'].max():.0f}")
print(f"  Mean: £{price_data['price_num'].mean():.0f}")
print(f"  Median: £{price_data['price_num'].median():.0f}")
print(f"  Std Dev: £{price_data['price_num'].std():.0f}")
print()

# ==================== 3. DATE SANITY ====================
print("=" * 80)
print("3. DATE SANITY CHECK (ready_to_leave_parsed_ts)")
print("=" * 80)
print("Checking for dates >30 days in past or >2 years in future")

# Convert to datetime for analysis - don't modify df yet
# First parse with UTC awareness
parsed_ts = pd.to_datetime(df['ready_to_leave_parsed_ts'], errors='coerce', utc=True)
# Remove timezone for easier calculation (only for those that parsed successfully)
parsed_ts_naive = parsed_ts.dt.tz_localize(None)

# Current date for reference
reference_date = pd.to_datetime('2026-01-22')
print(f"Reference date: {reference_date.strftime('%Y-%m-%d')}")

# Calculate days difference
days_from_ref = (reference_date - parsed_ts_naive).dt.days

# Check for issues
date_issues_mask = parsed_ts_naive.notna()
print(f"\nTotal rows with ready_to_leave_parsed_ts: {date_issues_mask.sum():,}")

# More than 30 days in the past
past_30_days_mask = (days_from_ref > 30) & date_issues_mask
print(f"\n• Dates MORE THAN 30 DAYS IN PAST: {past_30_days_mask.sum():,}")
if past_30_days_mask.sum() > 0:
    print("  Examples (worst cases):")
    worst_indices = days_from_ref[past_30_days_mask].nlargest(5).index
    for idx in worst_indices:
        days_val = days_from_ref.loc[idx]
        breed = df.loc[idx, 'breed']
        ts = parsed_ts_naive.loc[idx]
        print(f"    {days_val:.0f} days past - {breed}: {ts.strftime('%Y-%m-%d')}")

# More than 2 years in the future (730 days)
future_2_years_mask = (days_from_ref < -730) & date_issues_mask
print(f"\n• Dates MORE THAN 2 YEARS IN FUTURE: {future_2_years_mask.sum():,}")
if future_2_years_mask.sum() > 0:
    print("  Examples (worst cases):")
    worst_indices = days_from_ref[future_2_years_mask].nsmallest(5).index
    for idx in worst_indices:
        days_val = days_from_ref.loc[idx]
        breed = df.loc[idx, 'breed']
        ts = parsed_ts_naive.loc[idx]
        print(f"    {abs(days_val):.0f} days future - {breed}: {ts.strftime('%Y-%m-%d')}")

# Overall distribution
print(f"\nDate Distribution:")
print(f"  Earliest date: {parsed_ts_naive.min().strftime('%Y-%m-%d')}")
print(f"  Latest date: {parsed_ts_naive.max().strftime('%Y-%m-%d')}")
print(f"  Null/Missing: {df['ready_to_leave_parsed_ts'].isna().sum():,}")
print()

# ==================== 4. FILL RATES BY PLATFORM ====================
print("=" * 80)
print("4. FILL RATES BY PLATFORM (Key Fields)")
print("=" * 80)

key_fields = ['url', 'price_num', 'breed', 'ready_to_leave_parsed_ts', 
              'location', 'seller_name', 'is_breeder', 'rating', 'views_count_num']

platforms = df['platform'].unique()
fill_rate_results = []

for platform in sorted(platforms):
    platform_df = df[df['platform'] == platform]
    n_rows = len(platform_df)
    
    print(f"\n{platform.upper()} ({n_rows:,} rows):")
    for field in key_fields:
        if field in platform_df.columns:
            # For ready_to_leave_parsed_ts, parse timestamps to check for true nulls
            if field == 'ready_to_leave_parsed_ts':
                filled = pd.to_datetime(platform_df[field], errors='coerce', utc=True).notna().sum()
            else:
                filled = platform_df[field].notna().sum()
            
            pct = (filled / n_rows) * 100 if n_rows > 0 else 0
            print(f"  {field:30s}: {pct:5.1f}% ({filled:,}/{n_rows:,})")
            fill_rate_results.append({
                'platform': platform,
                'field': field,
                'filled': filled,
                'total': n_rows,
                'pct_filled': pct
            })
    
    # For ready_to_leave, show parse mode breakdown
    if 'ready_to_leave_parse_mode' in platform_df.columns:
        parsed_ts = pd.to_datetime(platform_df['ready_to_leave_parsed_ts'], errors='coerce', utc=True)
        filled = parsed_ts.notna().sum()
        if filled < n_rows:
            print(f"  Parse modes for remaining:")
            modes = platform_df[parsed_ts.isna()]['ready_to_leave_parse_mode'].value_counts()
            for mode, count in modes.items():
                if pd.isna(mode):
                    print(f"    - NULL: {count}")
                else:
                    print(f"    - {mode}: {count}")

print()

# ==================== 5. SAMPLE 5 ROWS FROM EACH PARSE_MODE ====================
print("=" * 80)
print("5. SAMPLE 5 ROWS FROM EACH PARSE_MODE")
print("=" * 80)

parse_modes = df['ready_to_leave_parse_mode'].unique()
print(f"Parse modes found: {sorted(parse_modes)}\n")

for mode in sorted(parse_modes):
    if pd.isna(mode):
        print(f"\nPARSE MODE: NULL ({len(df[df['ready_to_leave_parse_mode'].isna()]):,} rows)")
        sample = df[df['ready_to_leave_parse_mode'].isna()].head(5)
    else:
        mode_count = len(df[df['ready_to_leave_parse_mode'] == mode])
        print(f"\nPARSE MODE: {mode} ({mode_count:,} rows)")
        sample = df[df['ready_to_leave_parse_mode'] == mode].head(5)
    
    for idx, (i, row) in enumerate(sample.iterrows(), 1):
        print(f"\n  Sample {idx}:")
        print(f"    Platform: {row['platform']}")
        title = str(row['title']) if pd.notna(row['title']) else "N/A"
        print(f"    Title: {title[:60]}...")
        print(f"    Breed: {row['breed']}")
        print(f"    Ready to Leave: {row['ready_to_leave']}")
        print(f"    Ready to Leave (Parsed): {row['ready_to_leave_parsed_ts']}")
        print(f"    Parse Mode: {row['ready_to_leave_parse_mode']}")
        print(f"    Price: {row['price']}")
        location = str(row['location']) if pd.notna(row['location']) else "N/A"
        print(f"    Location: {location}")
        print(f"    URL: {row['url'][:70]}...")

print("\n" + "=" * 80)
print("DATA QUALITY CHECK COMPLETE")
print("=" * 80)
