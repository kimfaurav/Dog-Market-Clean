'''
CANONICAL METRICS - SINGLE SOURCE OF TRUTH
============================================

This module computes ALL metrics used across all slides from derived.csv.
Any slide that needs data should read from canonical_metrics.json.

KEY DEFINITIONS & RULES:
========================

SELLER IDENTIFICATION (seller_key = name + location):
  - Use BOTH seller_name and location to uniquely identify sellers
  - This avoids collisions: many "Sarah" exists across UK
  - Format: "Sarah|Birmingham" 
  - UNKNOWN names excluded from high-volume analysis

HIGH-VOLUME SELLERS (3+ listings):
  - Only breeder/seller listings (NOT rescues)
  - Rescue filter: user_type contains "rescue" OR seller_name contains "rescue" 
    OR (dogs >1 year old AND price <£500) [heuristic for rehoming]
  - License tracking: Measure if seller has ANY license_num on their listings
  - License % = (sellers with license / total sellers) * 100

LISTING FRESHNESS:
  - Age = days since published_at_ts
  - Categories: <7d, 7-30d, 30-90d, 90d+
  - Represents active inventory

PUPPY AGE DISTRIBUTION:
  - Calculated from date_of_birth when available
  - Buckets: <8w, 8-12w, 12-26w, 6-12mo, >1yr
  - <8w = illegal ready-to-leave (Lucy's Law violation)
  - Reference date: 2026-01-22

DEDUPLICATION:
  - Method: breed + location + price_band (£50 buckets)
  - Removes near-duplicates across same breeder
  - Keeps one listing per unique breed/location/price combo

ANNUALIZATION:
  - Formula: unique_puppies × (365/30) × 1.2 seasonality
  - Market share = annual / 946,000 UK estimate
'''
import pandas as pd
import json
from pathlib import Path
from datetime import timedelta
import re


def parse_relative_date(text, reference_date):
    """Parse relative date strings like '5 days ago' or '2 weeks ago'"""
    if pd.isna(text):
        return None
    text = str(text).lower().strip()
    match = re.match(r'(\d+)\s+(day|week|month)s?\s+ago', text)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'day':
            return reference_date - timedelta(days=num)
        if unit == 'week':
            return reference_date - timedelta(weeks=num)
        if unit == 'month':
            return reference_date - timedelta(days=num * 30)
    return None


def categorize_age(dob, ref_date='2026-01-22'):
    """Categorize puppy age into buckets."""
    if pd.isna(dob):
        return None
    birth = pd.to_datetime(dob)
    ref = pd.to_datetime(ref_date)
    age_days = (ref - birth).days
    age_weeks = age_days / 7
    if age_weeks < 8:
        return '<8'
    if age_weeks < 12:
        return '8-12'
    if age_weeks < 26:
        return '12-26'
    if age_weeks < 52:
        return '6-12mo'
    return '>1yr'


def compute_breed_stats(df):
    '''Compute top breeds by count and price.'''
    breed_counts = df[df['breed'] != 'Mixed Breed']['breed'].value_counts().head(10)
    total_non_mixed = len(df[df['breed'] != 'Mixed Breed'])
    top_by_count = []
    for breed, count in breed_counts.items():
        pct = round((count / total_non_mixed) * 100, 1)
        top_by_count.append({
            'breed': breed,
            'count': int(count),
            'share': pct
        })
    
    # Top breeds by average price
    breed_prices = df[df['price_num'].notna()].groupby('breed')['price_num'].agg(['mean', 'count'])
    breed_prices = breed_prices[breed_prices['count'] >= 5].sort_values('mean', ascending=False).head(10)
    top_by_price = []
    for breed, row in breed_prices.iterrows():
        top_by_price.append({
            'breed': breed,
            'avg_price': round(row['mean']),
            'count': int(row['count'])
        })
    
    return {
        'top_by_count': top_by_count,
        'top_by_price': top_by_price
    }


def compute_metrics():
    '''Compute all metrics from canonical derived.csv'''
    df = pd.read_csv('output/views/derived.csv', low_memory=False)
    
    # Seller key for deduplication
    df['seller_key'] = df['seller_name'].fillna('UNKNOWN') + '|' + df['location'].fillna('UNKNOWN')
    
    # Raw counts
    raw_listings = len(df)
    raw_puppies = int(df['total_available_num'].sum())
    raw_avg = raw_puppies / raw_listings
    
    # Deduplication using breed + location + price_band
    has_price = df[df['price_num'].notna()].copy()
    no_price = df[df['price_num'].isna()].copy()
    has_price['pb'] = (has_price['price_num'] / 50).round(0).astype(int)
    has_price['dk'] = has_price['breed'] + '|' + has_price['location'] + '|' + has_price['pb'].astype(str)
    unique_df = has_price.drop_duplicates(subset=['dk'], keep='first')
    unique_pups_priced = int(unique_df['total_available_num'].sum())
    unique_pups_no_price = int(no_price['total_available_num'].sum())
    unique_pups = unique_pups_priced + unique_pups_no_price
    unique_listings = len(unique_df) + len(no_price)
    dup_rows = raw_listings - unique_listings
    groups = has_price.groupby('dk').size()
    dup_groups = (groups > 1).sum()
    
    # Annualization
    annualized = int(unique_pups * 12.1667 * 1.2)
    market_share = (annualized / 946000) * 100
    
    # Platform breakdown
    platforms = {}
    for p in sorted(df['platform'].unique()):
        pdf = df[df['platform'] == p]
        pups = int(pdf['total_available_num'].sum())
        p_priced = pdf[pdf['price_num'].notna()].copy()
        p_priced['pb'] = (p_priced['price_num'] / 50).round(0).astype(int)
        p_priced['dk'] = p_priced['breed'] + '|' + p_priced['location'] + '|' + p_priced['pb'].astype(str)
        p_unique = p_priced['dk'].nunique() + len(pdf[pdf['price_num'].isna()])
        platforms[p] = {
            'listings': len(pdf),
            'puppies': pups,
            'unique': p_unique,
            'avg': round(pups / len(pdf), 1) if len(pdf) > 0 else 0,
            'share': round((pups / raw_puppies) * 100, 1) if raw_puppies > 0 else 0
        }
    
    # Cross-platform duplicates
    cross = {}
    for dk, cnt in groups.items():
        if cnt >= 2:
            cross[cnt] = cross.get(cnt, 0) + 1
    
    # Seller analysis (excluding rescues)
    rescue_mask = (
        df['user_type'].str.contains('rescue', case=False, na=False) | 
        df['seller_name'].fillna('').str.contains('rescue', case=False, na=False) | 
        ((df['age_days'] > 365) & (df['price_num'] < 500))
    )
    seller_df = df[(df['seller_key'] != 'UNKNOWN|UNKNOWN') & ~rescue_mask].copy()
    seller_counts = seller_df.groupby('seller_key').size()
    total_sellers = len(seller_counts)
    high_volume_keys = seller_counts[seller_counts >= 3].index.tolist()
    total_high_volume_global = len(high_volume_keys)
    total_high_volume = total_high_volume_global
    
    # Seller platforms breakdown
    seller_platforms = {}
    for p in sorted(df['platform'].unique()):
        p_sellers = seller_df[seller_df['platform'] == p]
        p_counts = p_sellers.groupby('seller_key').size()
        p_high_volume = p_counts[p_counts >= 3]
        sellers_cnt = len(p_high_volume)
        p_hv_keys = p_high_volume.index.tolist()
        p_hv_data = p_sellers[p_sellers['seller_key'].isin(p_hv_keys)]
        
        # License tracking for high-volume sellers
        if len(p_hv_data) > 0:
            license_sellers = p_hv_data.groupby('seller_key')['license_num'].apply(
                lambda x: x.notna().any()
            ).sum()
            license_pct = round((license_sellers / sellers_cnt) * 100, 1) if sellers_cnt > 0 else 0
        else:
            license_sellers = 0
            license_pct = 0
        
        seller_platforms[p] = {
            'sellers': sellers_cnt,
            'pct': round((sellers_cnt / total_high_volume) * 100, 1) if total_high_volume else 0,
            'license_sellers': int(license_sellers),
            'license_pct': license_pct
        }
    
    # Top sellers
    top_sellers = []
    for seller_key, count in seller_counts.sort_values(ascending=False).head(10).items():
        name, loc = seller_key.split('|', 1)
        s_df = seller_df[seller_df['seller_key'] == seller_key]
        s_platforms = sorted(s_df['platform'].unique())
        has_license = bool(s_df['license_num'].notna().any())
        top_sellers.append({
            'name': name,
            'location': loc,
            'listings': int(count),
            'platforms': list(s_platforms),
            'has_license': has_license
        })
    
    # Listing freshness
    df['published_dt'] = pd.to_datetime(df['published_at_ts'], errors='coerce')
    df['asof_dt'] = pd.to_datetime(df['asof_ts'], errors='coerce')
    
    for idx, row in df[df['published_dt'].isna() & df['published_at'].notna()].iterrows():
        parsed_date = parse_relative_date(row['published_at'], row['asof_dt'])
        if parsed_date:
            df.at[idx, 'published_dt'] = parsed_date
    
    reference_date = df['published_dt'].max()
    df['listing_age_days'] = (reference_date - df['published_dt']).dt.days
    
    freshness = {}
    for p in ('gumtree', 'pets4homes', 'freeads', 'foreverpuppy', 'preloved', 'puppies', 'petify'):
        pdf = df[df['platform'] == p].copy()
        if len(pdf) == 0:
            continue
        median_age = pdf['listing_age_days'].median()
        total = len(pdf)
        under_7 = (pdf['listing_age_days'] <= 7).sum()
        days_7_30 = ((pdf['listing_age_days'] > 7) & (pdf['listing_age_days'] <= 30)).sum()
        days_30_90 = ((pdf['listing_age_days'] > 30) & (pdf['listing_age_days'] <= 90)).sum()
        over_90 = (pdf['listing_age_days'] > 90).sum()
        freshness[p] = {
            'median_days': int(median_age) if pd.notna(median_age) else None,
            'total': int(total),
            'under_7d': int(under_7),
            'under_7d_pct': round((under_7 / total) * 100) if total > 0 else 0,
            '7_30d': int(days_7_30),
            '7_30d_pct': round((days_7_30 / total) * 100) if total > 0 else 0,
            '30_90d': int(days_30_90),
            '30_90d_pct': round((days_30_90 / total) * 100) if total > 0 else 0,
            'over_90d': int(over_90),
            'over_90d_pct': round((over_90 / total) * 100) if total > 0 else 0
        }
    
    # Puppy age distribution
    df['age_bucket'] = df['date_of_birth'].apply(categorize_age)
    age_data = {}
    for platform in sorted(df['platform'].unique()):
        platform_df = df[df['platform'] == platform]
        with_age = platform_df[platform_df['age_bucket'].notna()]
        if len(with_age) == 0:
            continue
        dist = with_age['age_bucket'].value_counts(normalize=True).sort_index() * 100
        
        # Calculate median weeks
        def calc_weeks(x):
            if pd.notna(x):
                return (pd.to_datetime('2026-01-22') - pd.to_datetime(x)).days / 7
            return None
        
        median_weeks = with_age['date_of_birth'].apply(calc_weeks).median()
        
        age_data[platform] = {
            'under_8w': round(dist.get('<8', 0)),
            '8-12w': round(dist.get('8-12', 0)),
            '12-26w': round(dist.get('12-26', 0)),
            '6-12mo': round(dist.get('6-12mo', 0)),
            'over_1yr': round(dist.get('>1yr', 0)),
            'median_weeks': round(median_weeks) if pd.notna(median_weeks) else None,
            'total_with_age': len(with_age)
        }
    
    # Puppies vs adults overall
    all_with_age = df[df['age_bucket'].notna()]
    if len(all_with_age) > 0:
        puppies_pct = (all_with_age['age_bucket'] != '>1yr').sum() / len(all_with_age) * 100
        puppies_vs_adults = {
            'total_with_age': len(all_with_age),
            'under_1yr': int((all_with_age['age_bucket'] != '>1yr').sum()),
            'under_1yr_pct': round(puppies_pct, 1),
            'over_1yr': int((all_with_age['age_bucket'] == '>1yr').sum()),
            'over_1yr_pct': round(100 - puppies_pct, 1)
        }
    else:
        puppies_vs_adults = {
            'total_with_age': 0,
            'under_1yr': 0,
            'under_1yr_pct': 0,
            'over_1yr': 0,
            'over_1yr_pct': 0
        }
    
    # Breed stats
    breed_stats = compute_breed_stats(df)
    
    # QA metrics
    qa = {
        'total_rows': raw_listings,
        'unique_after_dedupe': unique_listings,
        'duplicates_removed': dup_rows,
        'duplicate_groups': int(dup_groups),
        'sellers_total': total_sellers,
        'sellers_high_volume': total_high_volume,
        'platforms_count': len(platforms)
    }
    
    # Assemble final metrics
    metrics = {
        'summary': {
            'raw_listings': raw_listings,
            'raw_puppies': raw_puppies,
            'raw_avg_per_listing': round(raw_avg, 2),
            'unique_listings': unique_listings,
            'unique_puppies': unique_pups,
            'duplicates_removed': dup_rows,
            'annualized_puppies': annualized,
            'market_share_pct': round(market_share, 2)
        },
        'platforms': platforms,
        'cross_platform_duplicates': cross,
        'sellers': {
            'total': total_sellers,
            'high_volume': total_high_volume,
            'by_platform': seller_platforms,
            'top_10': top_sellers
        },
        'freshness': freshness,
        'age_distribution': age_data,
        'puppies_vs_adults': puppies_vs_adults,
        'breeds': breed_stats,
        'qa': qa
    }
    
    return metrics


def main():
    """Generate canonical_metrics.json from derived.csv"""
    print("Computing canonical metrics...")
    metrics = compute_metrics()
    
    output_path = Path('canonical_metrics.json')
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Written: {output_path}")
    print(f"  - {metrics['summary']['raw_listings']} raw listings")
    print(f"  - {metrics['summary']['unique_puppies']} unique puppies")
    print(f"  - {metrics['summary']['annualized_puppies']} annualized")
    print(f"  - {metrics['summary']['market_share_pct']:.2f}% market share")


if __name__ == '__main__':
    main()
