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
    """Parse relative date strings like '5 days ago', '2 weeks ago', or '12 hours ago'"""
    if pd.isna(text) or pd.isna(reference_date):
        return None
    text = str(text).lower().strip()
    match = re.match(r'(\d+)\s+(hour|day|week|month)s?\s+ago', text)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'hour':
            return reference_date - timedelta(hours=num)
        if unit == 'day':
            return reference_date - timedelta(days=num)
        if unit == 'week':
            return reference_date - timedelta(weeks=num)
        if unit == 'month':
            return reference_date - timedelta(days=num * 30)
    return None


def parse_age_string(age_str):
    """Parse age strings like '9 weeks', '3 months', '2 years', '12 days', '3½ months' into weeks."""
    if pd.isna(age_str):
        return None
    text = str(age_str).lower().strip()

    # Handle fractions like ½
    text = text.replace('½', '.5')

    # Match patterns like "9 weeks", "3 months", "2 years", "12 days"
    match = re.match(r'([\d.]+)\s*(day|week|month|year)s?', text)
    if match:
        num = float(match.group(1))
        unit = match.group(2)
        if unit == 'day':
            return num / 7  # Convert days to weeks
        if unit == 'week':
            return num
        if unit == 'month':
            return num * 4.33  # ~4.33 weeks per month
        if unit == 'year':
            return num * 52
    return None


def categorize_age(dob, ref_date='2026-01-22'):
    """Categorize puppy age into buckets based on date_of_birth."""
    if pd.isna(dob):
        return None
    try:
        birth = pd.to_datetime(dob)
        ref = pd.to_datetime(ref_date)
    except:
        return None
    age_days = (ref - birth).days
    age_weeks = age_days / 7
    return categorize_age_weeks(age_weeks)


def categorize_age_weeks(age_weeks):
    """Categorize age in weeks into buckets."""
    if pd.isna(age_weeks):
        return None
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
    '''Compute top breeds by puppy count and price.'''
    # Count actual puppies (not listings) using total_available_num
    # Fill NaN with 1 (assume at least 1 puppy per listing)
    df_breeds = df[df['breed'] != 'Mixed Breed'].copy()
    df_breeds['puppy_count'] = df_breeds['total_available_num'].fillna(1)

    # Sum puppies by breed
    breed_puppies = df_breeds.groupby('breed')['puppy_count'].sum().sort_values(ascending=False).head(10)
    total_puppies = df_breeds['puppy_count'].sum()

    top_by_count = []
    for breed, count in breed_puppies.items():
        pct = round((count / total_puppies) * 100, 1)
        top_by_count.append({
            'breed': breed,
            'count': int(count),
            'share': pct
        })
    
    # Top breeds by median price (more robust to outliers than mean)
    # Require minimum 10 listings for statistical significance
    breed_prices = df[df['price_num'].notna()].groupby('breed')['price_num'].agg(['median', 'mean', 'count'])
    breed_prices = breed_prices[breed_prices['count'] >= 10].sort_values('median', ascending=False).head(10)
    top_by_price = []
    for breed, row in breed_prices.iterrows():
        # Also get puppy count for this breed
        breed_puppies_count = df_breeds[df_breeds['breed'] == breed]['puppy_count'].sum()
        top_by_price.append({
            'breed': breed,
            'avg_price': round(row['median']),  # Using median
            'count': int(row['count']),  # Number of listings with price
            'puppies': int(breed_puppies_count)  # Number of puppies
        })
    
    return {
        'top_by_count': top_by_count,
        'top_by_price': top_by_price
    }


def infer_puppy_count(row):
    """
    Infer number of puppies from available fields.
    Priority:
      1. total_available_num if present and valid (1-15)
      2. males_available_num + females_available_num if valid (each <= 12)
      3. Parse sex field (e.g., "Male (2)", "2 male, 2 female", "Mixed Litter")
      4. Parse title for patterns like "X puppies", "litter of X"
      5. Fallback to 1

    Max realistic litter size capped at 15.
    """
    MAX_LITTER = 15

    # 1. Use total_available_num if valid (sanity: 1-15)
    total = row.get('total_available_num')
    if pd.notna(total) and 1 <= total <= MAX_LITTER:
        return int(total)

    # 2. Use males + females if available (sanity: each <= 12, avoids price misparses)
    males = row.get('males_available_num')
    females = row.get('females_available_num')
    males = males if pd.notna(males) and males <= 12 else 0
    females = females if pd.notna(females) and females <= 12 else 0
    if males + females > 0:
        return min(int(males + females), MAX_LITTER)

    # 3. Parse sex field
    sex = str(row.get('sex', '')).lower()
    if sex and sex != 'nan':
        # Pattern: "male (2)" or "female (3)"
        match = re.search(r'\((\d+)\)', sex)
        if match:
            count = int(match.group(1))
            if 1 <= count <= MAX_LITTER:
                return count
        # Pattern: "2 male, 2 female" or "1 male, 1 female"
        match = re.search(r'(\d+)\s*male.*?(\d+)\s*female', sex)
        if match:
            count = int(match.group(1)) + int(match.group(2))
            if 2 <= count <= MAX_LITTER:
                return count
        match = re.search(r'(\d+)\s*female.*?(\d+)\s*male', sex)
        if match:
            count = int(match.group(1)) + int(match.group(2))
            if 2 <= count <= MAX_LITTER:
                return count
        # "Mixed Litter" or "Mixed" implies at least 2
        if 'mixed' in sex:
            return 2

    # 4. Parse title for puppy counts
    title = str(row.get('title', '')).lower()
    if title and title != 'nan':
        # Word numbers to digits
        word_nums = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                     'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
        for word, num in word_nums.items():
            if word in title and 2 <= num <= MAX_LITTER:
                # Check it's followed by puppy-related words
                if re.search(rf'\b{word}\b.*(?:puppy|puppies|pups|pup|boys?|girls?|males?|females?|litter|remaining|left|available)', title):
                    return num

        # Patterns in priority order
        patterns = [
            # "litter of 8", "litter of 8 puppies"
            (r'litter\s*of\s*(\d+)', 1),
            # "have 4 american bulldog puppies", "got 3 pups"
            (r'\b(?:have|got|selling)\s+(\d+)\s+\w+', 1),
            # "8 cockapoo puppies", "4 pups available"
            (r'\b(\d+)\s+\w+\s*(?:puppy|puppies|pups)\b', 1),
            # "3 puppies", "5 pups left"
            (r'\b(\d+)\s*(?:puppy|puppies|pups|pup)\b', 1),
            # "3 beautiful king charles puppies", "2 stunning boys"
            (r'\b(\d+)\s+(?:beautiful|gorgeous|stunning|lovely|adorable|amazing)\s+.*?(?:puppy|puppies|pups|boys?|girls?)', 1),
            # "only 1 left", "only 2 remaining"
            (r'\bonly\s+(\d+)\s+(?:\w+\s+)?(?:left|remaining|available)', 1),
            # "2 left", "3 remaining" (but not "2 weeks left")
            (r'\b(\d+)\s+(?:left|remaining)\b(?!\s*(?:week|month|year|day))', 1),
            # "last 2 from litter"
            (r'\blast\s+(\d+)\b', 1),
            # "3 boys and 2 girls", "2 males 1 female"
            (r'\b(\d+)\s*(?:boys?|males?)\s*(?:and|&|,)?\s*(\d+)\s*(?:girls?|females?)', 2),
            (r'\b(\d+)\s*(?:girls?|females?)\s*(?:and|&|,)?\s*(\d+)\s*(?:boys?|males?)', 2),
        ]

        for pattern, groups in patterns:
            match = re.search(pattern, title)
            if match:
                if groups == 1:
                    count = int(match.group(1))
                else:
                    count = int(match.group(1)) + int(match.group(2))
                if 1 <= count <= MAX_LITTER:
                    return count

    # 5. Platform-specific defaults (Champdogs behaves like Kennel Club - litter listings)
    platform = str(row.get('platform', '')).lower()
    if platform == 'champdogs':
        return 6  # Assume similar to Kennel Club avg

    # 6. Fallback
    return 1


def compute_metrics():
    '''Compute all metrics from canonical derived.csv'''
    df = pd.read_csv('output/views/derived.csv', low_memory=False)

    # Seller key for deduplication
    df['seller_key'] = df['seller_name'].fillna('UNKNOWN') + '|' + df['location'].fillna('UNKNOWN')

    # Exclude Petify from seller analysis (only has initials, not usable for seller identification)
    df.loc[df['platform'] == 'petify', 'seller_key'] = 'UNKNOWN|UNKNOWN'

    # Map Preloved's user_type='Licensed Breeder' to license_num for consistent tracking
    licensed_breeder_mask = df['user_type'] == 'Licensed Breeder'
    df.loc[licensed_breeder_mask & df['license_num'].isna(), 'license_num'] = 'LICENSED'

    # Infer puppy count from multiple sources
    df['total_available_num'] = df.apply(infer_puppy_count, axis=1)

    # Calculate listing age early (needed for stale removal)
    df['published_dt'] = pd.to_datetime(df['published_at_ts'], errors='coerce')
    df['asof_dt'] = pd.to_datetime(df['asof_ts'], errors='coerce')

    for idx, row in df[df['published_dt'].isna() & df['published_at'].notna()].iterrows():
        parsed_date = parse_relative_date(row['published_at'], row['asof_dt'])
        if parsed_date:
            df.at[idx, 'published_dt'] = parsed_date

    # Handle petify: load posted_ago from raw CSV (not in derived.csv)
    try:
        petify_raw = pd.read_csv('Input/Raw CSVs/petify_data_clean copy.csv', low_memory=False)
        petify_raw['asof_dt'] = df[df['platform'] == 'petify']['asof_dt'].iloc[0] if len(df[df['platform'] == 'petify']) > 0 else pd.NaT
        # Create lookup by URL
        petify_dates = {}
        for _, row in petify_raw[petify_raw['posted_ago'].notna()].iterrows():
            parsed = parse_relative_date(row['posted_ago'], petify_raw['asof_dt'].iloc[0])
            if parsed:
                petify_dates[row['url']] = parsed
        # Apply to main df
        petify_mask = (df['platform'] == 'petify') & df['published_dt'].isna()
        for idx, row in df[petify_mask].iterrows():
            if row['url'] in petify_dates:
                df.at[idx, 'published_dt'] = petify_dates[row['url']]
    except Exception as e:
        print(f"Warning: Could not load petify dates: {e}")

    # Note: champdogs and kennel_club don't have listing dates in their data
    # (they have DOB which is different). Treat as fresh by default.

    reference_date = df['published_dt'].max()
    df['listing_age_days'] = (reference_date - df['published_dt']).dt.days

    # Raw counts (before filtering non-sales)
    raw_listings_before_filter = len(df)

    # Remove non-dog-sale listings
    # 1. Stud services (breeding services, not dogs for sale)
    stud_mask = df['title'].str.contains(r'\bat stud\b|\bstanding at stud\b|\bstud service|\bstud dog\b',
                                          case=False, na=False, regex=True)
    # 2. Lost/Missing dogs
    lost_mask = df['title'].str.contains(r'\bmissing\b(?! out)|\blost dog',
                                          case=False, na=False, regex=True)
    # 3. Merchandise (low price + accessory keywords)
    merch_mask = (df['price_num'] < 50) & df['title'].str.contains(
        r'\bmug[s]?\b|\bmuzzle|\bshoe[s]?\b|\bshirt|\bcanvas|\bprint|\bcleaning|\bposter|\bhoodie',
        case=False, na=False, regex=True)
    # 4. Genuine "wanted" ads (looking to buy, not "home wanted" which is selling)
    wanted_mask = df['title'].str.contains(r'^wanted\b|dog share wanted|small dog wanted|puppy wanted',
                                            case=False, na=False, regex=True)

    # Combine all non-sale masks
    non_sale_mask = stud_mask | lost_mask | merch_mask | wanted_mask
    non_sale_removed = int(non_sale_mask.sum())

    # Filter out non-sales
    df = df[~non_sale_mask].copy()

    # Raw counts (after filtering)
    raw_listings = len(df)
    raw_puppies = int(df['total_available_num'].sum())
    raw_avg = raw_puppies / raw_listings

    # Deduplication with two rules:
    # 1. Scrape artifacts: same URL (true duplicates from re-scraping)
    # 2. Cross-platform: same breed + location + price_band (cross-posting)
    has_price = df[df['price_num'].notna()].copy()
    no_price = df[df['price_num'].isna()].copy()
    has_price['pb'] = (has_price['price_num'] / 50).round(0).astype(int)
    has_price['cross_dk'] = has_price['breed'] + '|' + has_price['location'].fillna('') + '|' + has_price['pb'].astype(str)

    # Extract listing ID from URL for platforms that use them
    def extract_listing_id(url):
        if pd.isna(url):
            return None
        url = str(url)
        # Gumtree: ends with /123456789
        match = re.search(r'/(\d{7,})/?$', url)
        return match.group(1) if match else url  # Fall back to full URL

    # Mark scrape artifacts (same URL or same extracted listing ID)
    has_price['listing_id'] = has_price['url'].apply(extract_listing_id)
    has_price['is_within_dup'] = has_price.duplicated(subset=['listing_id'], keep='first') & has_price['listing_id'].notna()
    within_dups_priced = int(has_price['is_within_dup'].sum())

    # Mark scrape artifacts for no_price too
    no_price['listing_id'] = no_price['url'].apply(extract_listing_id)
    no_price['is_within_dup'] = no_price.duplicated(subset=['listing_id'], keep='first') & no_price['listing_id'].notna()
    within_dups_no_price = int(no_price['is_within_dup'].sum())
    within_dups = within_dups_priced + within_dups_no_price

    # Remove scrape artifacts first
    after_within = has_price[~has_price['is_within_dup']].copy()
    no_price_after_within = no_price[~no_price['is_within_dup']].copy()

    # Mark cross-platform duplicates (same breed+loc+price on different platforms)
    # For each cross_dk that appears on multiple platforms, keep first row, mark rest as dups
    after_within['is_cross_dup'] = False
    for dk, group in after_within.groupby('cross_dk'):
        if group['platform'].nunique() > 1:
            # Keep first occurrence, mark all others as cross-platform dups
            for idx in group.index[1:]:
                after_within.loc[idx, 'is_cross_dup'] = True

    cross_dups = int(after_within['is_cross_dup'].sum())

    # Remove stale listings (>180 days / 6 months old)
    after_cross = after_within[~after_within['is_cross_dup']].copy()
    STALE_THRESHOLD_DAYS = 180
    after_cross['is_stale'] = after_cross['listing_age_days'].fillna(0) > STALE_THRESHOLD_DAYS
    stale_removed = int(after_cross['is_stale'].sum())

    # Also remove stale from no_price listings (after within-platform dedup)
    no_price_after_within['is_stale'] = no_price_after_within['listing_age_days'].fillna(0) > STALE_THRESHOLD_DAYS
    stale_removed_no_price = int(no_price_after_within['is_stale'].sum())
    stale_removed_total = stale_removed + stale_removed_no_price

    # Count duplicate groups for QA
    # Scrape artifacts: count of listing_ids that appear more than once
    within_groups_priced = int((has_price[has_price['listing_id'].notna()].groupby('listing_id').size() > 1).sum())
    within_groups_no_price = int((no_price[no_price['listing_id'].notna()].groupby('listing_id').size() > 1).sum())
    within_groups = within_groups_priced + within_groups_no_price
    # Cross-platform: count of cross_dk values that appear on multiple platforms
    cross_groups = sum(1 for dk, g in after_within.groupby('cross_dk') if g['platform'].nunique() > 1)
    dup_groups = within_groups + cross_groups

    # Final unique set (after removing within-dups, cross-dups, and stale)
    unique_df = after_cross[~after_cross['is_stale']]
    unique_no_price = no_price_after_within[~no_price_after_within['is_stale']]
    unique_pups_priced = int(unique_df['total_available_num'].sum())
    unique_pups_no_price = int(unique_no_price['total_available_num'].sum())
    unique_pups = unique_pups_priced + unique_pups_no_price
    unique_listings = len(unique_df) + len(unique_no_price)
    total_removed = within_dups + cross_dups + stale_removed_total
    
    # Annualization based on 29-day average listing age
    # 365/29 = 12.586 turnovers per year, × 1.2 seasonality adjustment
    annualized = int(unique_pups * (365/29) * 1.2)
    market_share = (annualized / 946000) * 100
    
    # Platform breakdown - use same dedup logic as within-platform (seller_key + title)
    platforms = {}
    for p in sorted(df['platform'].unique()):
        pdf = df[df['platform'] == p].copy()
        pups = int(pdf['total_available_num'].sum())
        # Calculate unique using seller_key + title (same as within-platform dedup)
        pdf['within_dk'] = pdf['seller_key'] + '|' + pdf['title'].fillna('')
        p_unique = pdf['within_dk'].nunique()
        platforms[p] = {
            'listings': len(pdf),
            'puppies': pups,
            'unique': p_unique,
            'avg': round(pups / len(pdf), 1) if len(pdf) > 0 else 0,
            'share': round((pups / raw_puppies) * 100, 1) if raw_puppies > 0 else 0
        }
    
    # Cross-platform duplicates - count by number of platforms
    cross = {}
    platform_counts = after_within.groupby('cross_dk')['platform'].nunique()
    for dk, num_platforms in platform_counts.items():
        if num_platforms >= 2:
            key = int(num_platforms)
            cross[key] = cross.get(key, 0) + 1

    # Platform pair overlap - count shared listings between each pair
    from itertools import combinations
    pair_counts = {}
    for dk, group in after_within.groupby('cross_dk'):
        plats = group['platform'].unique()
        if len(plats) >= 2:
            for p1, p2 in combinations(sorted(plats), 2):
                pair_key = f"{p1}|{p2}"
                pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1

    # Calculate percentages (overlap / smaller platform's unique count)
    platform_pair_overlap = []
    for pair_key, count in sorted(pair_counts.items(), key=lambda x: -x[1]):
        p1, p2 = pair_key.split('|')
        p1_unique = platforms.get(p1, {}).get('unique', 1)
        p2_unique = platforms.get(p2, {}).get('unique', 1)
        smaller = min(p1_unique, p2_unique)
        pct = round(count / smaller * 100) if smaller > 0 else 0
        platform_pair_overlap.append({
            'pair': pair_key,
            'platforms': [p1, p2],
            'count': count,
            'pct': pct
        })

    # Seller analysis (including rescues)
    rescue_mask = (
        df['user_type'].str.contains('rescue', case=False, na=False) |
        df['seller_name'].fillna('').str.contains('rescue', case=False, na=False)
    )

    # All sellers (including rescues, for slide 6)
    all_seller_counts = df.groupby('seller_key').size()
    total_sellers = len(all_seller_counts)
    one_listing_sellers = (all_seller_counts == 1).sum()
    pct_one_listing = round(one_listing_sellers / total_sellers * 100) if total_sellers > 0 else 0

    # Rescue count
    rescue_sellers = df[rescue_mask]['seller_key'].nunique()

    # Known sellers (excluding UNKNOWN for max/top calculations)
    known_mask = ~df['seller_key'].str.contains('UNKNOWN', case=False, na=False)
    known_df = df[known_mask].copy()

    # High volume sellers (3+ listings, excluding rescues - for slide 7)
    non_rescue_df = df[~rescue_mask & (df['seller_key'] != 'UNKNOWN|UNKNOWN')].copy()
    non_rescue_counts = non_rescue_df.groupby('seller_key').size()
    high_volume_keys = non_rescue_counts[non_rescue_counts >= 3].index.tolist()
    total_high_volume = len(high_volume_keys)

    # Per-platform seller stats (for slide 6)
    seller_platforms = {}
    for p in sorted(df['platform'].unique()):
        pdf = df[df['platform'] == p]
        p_counts = pdf.groupby('seller_key').size()
        p_total = len(p_counts)
        p_one_listing = (p_counts == 1).sum()
        p_pct_one = round(p_one_listing / p_total * 100) if p_total > 0 else 0

        # Max from known sellers only
        known_pdf = known_df[known_df['platform'] == p]
        known_counts = known_pdf.groupby('seller_key').size()
        p_max = int(known_counts.max()) if len(known_counts) > 0 else 0

        # High-volume sellers (for slide 7)
        p_non_rescue = non_rescue_df[non_rescue_df['platform'] == p]
        p_nr_counts = p_non_rescue.groupby('seller_key').size()
        p_hv = p_nr_counts[p_nr_counts >= 3]
        hv_count = len(p_hv)

        # License tracking for high-volume sellers
        if hv_count > 0:
            p_hv_keys = p_hv.index.tolist()
            p_hv_data = p_non_rescue[p_non_rescue['seller_key'].isin(p_hv_keys)]
            license_sellers = p_hv_data.groupby('seller_key')['license_num'].apply(
                lambda x: x.notna().any()
            ).sum()
            license_pct = round((license_sellers / hv_count) * 100, 1) if hv_count > 0 else 0
        else:
            license_sellers = 0
            license_pct = 0

        seller_platforms[p] = {
            'total_sellers': p_total,
            'pct_one_listing': p_pct_one,
            'max_listings': p_max,
            'high_volume': hv_count,
            'hv_pct': round((hv_count / total_high_volume) * 100, 1) if total_high_volume else 0,
            'license_sellers': int(license_sellers),
            'license_pct': license_pct
        }

    # Top 10 sellers (excluding UNKNOWN, including rescues)
    known_counts = known_df.groupby('seller_key').size()
    top_sellers = []
    for seller_key, count in known_counts.sort_values(ascending=False).head(10).items():
        name, loc = seller_key.split('|', 1)
        s_df = known_df[known_df['seller_key'] == seller_key]
        s_platforms = sorted(s_df['platform'].unique())
        has_license = bool(s_df['license_num'].notna().any())
        is_rescue = bool(s_df['user_type'].str.contains('rescue', case=False, na=False).any() or 'rescue' in name.lower())
        top_sellers.append({
            'name': name,
            'location': loc,
            'listings': int(count),
            'platforms': list(s_platforms),
            'has_license': has_license,
            'is_rescue': is_rescue
        })
    
    # Listing freshness (date columns already calculated earlier for stale removal)
    freshness = {}
    for p in ('gumtree', 'pets4homes', 'freeads', 'foreverpuppy', 'preloved', 'puppies', 'petify', 'gundogs_direct'):
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
    
    # Puppy age distribution - use date_of_birth OR age string column
    # First, compute age_weeks from date_of_birth where available
    def calc_weeks_from_dob(x):
        if pd.notna(x):
            try:
                return (pd.to_datetime('2026-01-22') - pd.to_datetime(x)).days / 7
            except:
                return None
        return None

    df['age_weeks_from_dob'] = df['date_of_birth'].apply(calc_weeks_from_dob)

    # Parse age string column for platforms that use it
    df['age_weeks_from_str'] = df['age'].apply(parse_age_string)

    # Combine: prefer date_of_birth, fall back to age string
    df['age_weeks'] = df['age_weeks_from_dob'].fillna(df['age_weeks_from_str'])
    df['age_bucket'] = df['age_weeks'].apply(categorize_age_weeks)

    age_data = {}
    for platform in sorted(df['platform'].unique()):
        platform_df = df[df['platform'] == platform]
        with_age = platform_df[platform_df['age_bucket'].notna()]
        if len(with_age) == 0:
            continue
        dist = with_age['age_bucket'].value_counts(normalize=True).sort_index() * 100

        median_weeks = with_age['age_weeks'].median()

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
    
    # 8-week regulation compliance (ready-to-leave enforcement)
    under_8w = df[df['age_bucket'] == '<8']
    eight_week_regulation = {}
    for platform in ['pets4homes', 'gumtree', 'freeads']:
        pf = under_8w[under_8w['platform'] == platform]
        total = len(pf)
        if total == 0:
            continue
        has_ready = pf['ready_to_leave'].notna().sum()
        has_future = (pf['days_until_ready'] > 0).sum()
        no_ready = pf['ready_to_leave'].isna().sum()

        eight_week_regulation[platform] = {
            'total_under_8w': int(total),
            'has_ready_to_leave': int(has_ready),
            'has_future_date': int(has_future),
            'pct_protected': round(100 * has_future / total) if total > 0 else 0,
            'no_ready_date': int(no_ready)
        }

    # Breed stats
    breed_stats = compute_breed_stats(df)
    
    # Geography metrics
    def extract_city(loc):
        if pd.isna(loc) or loc == '':
            return None
        loc = str(loc).strip()
        if ',' in loc:
            return loc.split(',')[0].strip()
        return loc

    def extract_region(loc):
        if pd.isna(loc) or loc == '':
            return None
        loc = str(loc).strip()
        if ',' in loc:
            return loc.split(',', 1)[1].strip()
        return None

    df['city'] = df['location'].apply(extract_city)
    df['region'] = df['location'].apply(extract_region)

    # Top cities by dog count
    city_stats = df[df['city'].notna()].groupby('city').agg({
        'total_available_num': 'sum',
        'url': 'count'
    }).rename(columns={'total_available_num': 'dogs', 'url': 'listings'})
    city_stats['dogs'] = city_stats['dogs'].astype(int)
    city_stats = city_stats.sort_values('dogs', ascending=False)

    top_cities = []
    for city, row in city_stats.head(10).iterrows():
        top_cities.append({
            'city': city,
            'dogs': int(row['dogs']),
            'listings': int(row['listings'])
        })

    # Regional breakdown (UK regions)
    region_stats = df[df['region'].notna()].groupby('region').agg({
        'total_available_num': 'sum',
        'url': 'count'
    }).rename(columns={'total_available_num': 'dogs', 'url': 'listings'})
    region_stats['dogs'] = region_stats['dogs'].astype(int)
    region_stats = region_stats.sort_values('dogs', ascending=False)

    top_regions = []
    for region, row in region_stats.head(12).iterrows():
        top_regions.append({
            'region': region,
            'dogs': int(row['dogs']),
            'listings': int(row['listings'])
        })

    # Wisbech hotspot analysis
    wisbech_df = df[df['city'] == 'Wisbech']
    wisbech_dogs = int(wisbech_df['total_available_num'].sum())
    wisbech_listings = len(wisbech_df)
    wisbech_sellers = wisbech_df['seller_key'].nunique()
    wisbech_avg = round(wisbech_dogs / wisbech_listings, 1) if wisbech_listings > 0 else 0

    geography = {
        'top_cities': top_cities,
        'top_regions': top_regions,
        'hotspot': {
            'city': 'Wisbech',
            'region': 'Cambridgeshire',
            'dogs': wisbech_dogs,
            'listings': wisbech_listings,
            'sellers': wisbech_sellers,
            'avg_per_listing': wisbech_avg
        }
    }

    # QA metrics
    qa = {
        'total_rows': raw_listings,
        'unique_after_dedupe': unique_listings,
        'duplicates_removed': total_removed,
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
            'duplicates_removed': total_removed,
            'within_platform_dups': within_dups,
            'cross_platform_dups': cross_dups,
            'stale_removed': stale_removed_total,
            'non_sale_removed': non_sale_removed,
            'annualized_puppies': annualized,
            'market_share_pct': round(market_share, 2)
        },
        'platforms': platforms,
        'cross_platform_duplicates': cross,
        'platform_pair_overlap': platform_pair_overlap,
        'sellers': {
            'total': total_sellers,
            'pct_one_listing': pct_one_listing,
            'rescue_count': rescue_sellers,
            'high_volume': total_high_volume,
            'by_platform': seller_platforms,
            'top_10': top_sellers
        },
        'freshness': freshness,
        'age_distribution': age_data,
        'puppies_vs_adults': puppies_vs_adults,
        'eight_week_regulation': eight_week_regulation,
        'breeds': breed_stats,
        'geography': geography,
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
