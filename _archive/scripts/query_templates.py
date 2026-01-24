#!/usr/bin/env python3
"""
Common Query Templates for Dog Market Analysis

Copy and modify these as starting points for your analysis
"""

import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

print("=" * 80)
print("COMMON QUERY TEMPLATES")
print("=" * 80)

# ============================================================================
# 1. BREED ANALYSIS
# ============================================================================
print("\n1. TOP BREEDS AND PRICING\n")

breed_stats = derived.groupby('breed').agg({
    'price_num': ['count', 'mean', 'median', 'std'],
    'url': 'count'
}).round(2)

breed_stats.columns = ['_count', 'avg_price', 'median_price', 'std_price', 'listings']
breed_stats = breed_stats[breed_stats['listings'] > 10].sort_values('listings', ascending=False)

print(breed_stats.head(10))
print("\nCode:")
print("""
breed_stats = derived.groupby('breed').agg({
    'price_num': ['count', 'mean', 'median'],
}).round(2)
breed_stats = breed_stats[breed_stats['price_num']['count'] > 10]
breed_stats.sort_values(('price_num', 'mean'), ascending=False).head(10)
""")

# ============================================================================
# 2. PLATFORM COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("\n2. PLATFORM PRICE COMPARISON\n")

platform_price = derived.groupby('platform').agg({
    'price_num': ['count', 'mean', 'median'],
}).round(0)

platform_price.columns = ['listings', 'avg_price', 'median_price']
platform_price = platform_price.sort_values('listings', ascending=False)

print(platform_price)
print("\nCode:")
print("""
platform_price = derived.groupby('platform').agg({
    'price_num': ['count', 'mean', 'median']
}).round(0)
""")

# ============================================================================
# 3. LOCATION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("\n3. PRICE BY LOCATION (TOP 10)\n")

location_price = derived.groupby('location').agg({
    'price_num': ['count', 'mean', 'median'],
}).round(0)

location_price.columns = ['listings', 'avg_price', 'median_price']
location_price = location_price[location_price['listings'] > 5].sort_values('listings', ascending=False)

print(location_price.head(10))
print("\nCode:")
print("""
location_price = derived.groupby('location').agg({
    'price_num': ['count', 'mean', 'median']
}).round(0)
location_price = location_price[location_price['listings'] > 5]
""")

# ============================================================================
# 4. HEALTH DATA COVERAGE
# ============================================================================
print("\n" + "=" * 80)
print("\n4. HEALTH DATA BY PLATFORM\n")

health_coverage = derived.groupby('platform').agg({
    'microchipped': lambda x: (x.notna().sum() / len(x) * 100).round(1),
    'vaccinated': lambda x: (x.notna().sum() / len(x) * 100).round(1),
    'health_checked': lambda x: (x.notna().sum() / len(x) * 100).round(1),
})

health_coverage.columns = ['% Microchipped', '% Vaccinated', '% Health Checked']

print(health_coverage.sort_values('% Microchipped', ascending=False))
print("\nCode:")
print("""
health_coverage = derived.groupby('platform').agg({
    'microchipped': lambda x: (x.notna().sum() / len(x) * 100).round(1),
    'vaccinated': lambda x: (x.notna().sum() / len(x) * 100).round(1),
})
""")

# ============================================================================
# 5. AVAILABILITY ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("\n5. AVAILABILITY BY PLATFORM\n")

avail = df.groupby('platform').agg({
    'ready_to_leave_parse_mode': 'value_counts'
})

print("Ready-to-leave parse modes:")
print(derived['ready_to_leave_parse_mode'].value_counts())
print("\nCode:")
print("""
avail_modes = derived.groupby('platform')['ready_to_leave_parse_mode'].value_counts()
avail_modes.unstack(fill_value=0)
""")

# ============================================================================
# 6. SELLER ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("\n6. TOP SELLERS\n")

# Create unique seller ID
df['seller_id'] = df['seller_name'].fillna('') + ' | ' + df['location'].fillna('')

top_sellers = df['seller_id'].value_counts().head(10)
print(top_sellers)
print("\nCode:")
print("""
df['seller_id'] = df['seller_name'].fillna('') + ' | ' + df['location'].fillna('')
top_sellers = df['seller_id'].value_counts().head(10)
""")

# ============================================================================
# 7. PRICE OUTLIERS
# ============================================================================
print("\n" + "=" * 80)
print("\n7. PRICE OUTLIERS\n")

q1 = derived['price_num'].quantile(0.25)
q3 = derived['price_num'].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outliers = derived[(derived['price_num'] < lower) | (derived['price_num'] > upper)]

print(f"Q1: £{q1:.0f}, Q3: £{q3:.0f}, IQR: £{iqr:.0f}")
print(f"Outlier range: < £{lower:.0f} or > £{upper:.0f}")
print(f"Outliers: {len(outliers)} ({len(outliers)/len(derived)*100:.1f}%)")
print("\nCode:")
print("""
q1 = derived['price_num'].quantile(0.25)
q3 = derived['price_num'].quantile(0.75)
iqr = q3 - q1
outliers = derived[(derived['price_num'] < q1 - 1.5*iqr) | 
                   (derived['price_num'] > q3 + 1.5*iqr)]
""")

# ============================================================================
# 8. HEALTH VS PRICE
# ============================================================================
print("\n" + "=" * 80)
print("\n8. DOES MICROCHIPPING CORRELATE WITH PRICE?\n")

# Health status vs price
microchip_price = derived[derived['microchipped'].notna()].groupby('microchipped')['price_num'].agg(['count', 'mean', 'median'])
print(microchip_price.round(0))
print("\nCode:")
print("""
microchip_price = derived[derived['microchipped'].notna()].groupby('microchipped')['price_num'].agg(['count', 'mean'])
microchip_price.round(0)
""")

# ============================================================================
# 9. AGE DISTRIBUTION
# ============================================================================
print("\n" + "=" * 80)
print("\n9. PUPPY AGE DISTRIBUTION\n")

age_stats = derived['age_days'].describe().round(0)
print(age_stats)
print("\nCode:")
print("""
age_stats = derived['age_days'].describe()
# Age categories
young = derived[derived['age_days'] < 42]  # < 6 weeks
ready = derived[(derived['age_days'] >= 42) & (derived['age_days'] <= 90)]  # 6-12 weeks
older = derived[derived['age_days'] > 90]  # > 12 weeks
""")

# ============================================================================
# 10. TIME SERIES
# ============================================================================
print("\n" + "=" * 80)
print("\n10. LISTINGS OVER TIME\n")

derived_copy = derived.copy()
derived_copy['published_date'] = pd.to_datetime(derived_copy['published_at_ts'], errors='coerce')
listings_by_date = derived_copy.groupby(derived_copy['published_date'].dt.date).size()

print(f"Listings by date (last 10 days):")
print(listings_by_date.tail(10))
print("\nCode:")
print("""
derived['published_date'] = pd.to_datetime(derived['published_at_ts'], errors='coerce')
listings_by_date = derived.groupby(derived['published_date'].dt.date).size()
listings_by_date.plot()
""")

print("\n" + "=" * 80)
print("\nTHESE ARE TEMPLATES - MODIFY FOR YOUR SPECIFIC QUESTIONS")
print("=" * 80)
