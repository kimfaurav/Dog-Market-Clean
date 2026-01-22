#!/usr/bin/env python3
"""
Comprehensive Data Quality Audit
Checks for non-dogs, corrupt data, duplicates, and anomalies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load data
facts = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

print("=" * 100)
print("COMPREHENSIVE DATA QUALITY AUDIT")
print("=" * 100)

print(f"\nDataset: {len(facts):,} records across 9 platforms\n")

# ============================================================================
# 1. DUPLICATE DETECTION
# ============================================================================
print("\n" + "=" * 100)
print("1. DUPLICATE DETECTION")
print("=" * 100)

# Check URL duplicates
url_dupes = facts['url'].value_counts()
url_dupes_count = (url_dupes > 1).sum()
total_dup_urls = url_dupes[url_dupes > 1].sum()

print(f"\nURL Duplicates: {url_dupes_count} URLs appear {int(url_dupes[url_dupes > 1].sum()) - url_dupes_count} times")
if url_dupes_count > 0:
    print(f"  → {total_dup_urls} records are duplicates of {url_dupes_count} unique URLs")
    print(f"  → Top duplicated URLs:")
    for url, count in url_dupes[url_dupes > 1].head(5).items():
        platform = facts[facts['url'] == url]['platform'].iloc[0]
        print(f"     {platform}: {count} copies of {url[:60]}...")

# Check for completely identical rows
complete_dupes = facts.duplicated().sum()
print(f"\nCompletely identical rows: {complete_dupes}")

# ============================================================================
# 2. NON-DOG DETECTION
# ============================================================================
print("\n" + "=" * 100)
print("2. NON-DOG DETECTION")
print("=" * 100)

# Check for unusual breeds/titles
non_dog_keywords = [
    'cat', 'puppy mill', 'not a dog', 'guinea pig', 'hamster', 'rabbit', 
    'bird', 'fish', 'reptile', 'test', 'spam', 'scam', 'fake', 'error',
    'null', 'undefined', 'n/a', 'na', 'xxx', '---', '???', '***'
]

suspicious_breeds = []
for idx, row in facts.iterrows():
    breed = str(row['breed']).lower() if pd.notna(row['breed']) else ''
    title = str(row['title']).lower() if pd.notna(row['title']) else ''
    
    for keyword in non_dog_keywords:
        if keyword in breed or keyword in title:
            suspicious_breeds.append({
                'url': row['url'],
                'platform': row['platform'],
                'breed': row['breed'],
                'title': row['title'],
                'keyword': keyword
            })
            break

print(f"\nSuspicious entries (possible non-dogs): {len(suspicious_breeds)}")
if suspicious_breeds:
    print("\nTop suspicious entries:")
    for entry in suspicious_breeds[:10]:
        print(f"  • {entry['platform']}: '{entry['breed']}' - {entry['title'][:50]}")
    if len(suspicious_breeds) > 10:
        print(f"  ... and {len(suspicious_breeds) - 10} more")

# ============================================================================
# 3. PRICE ANOMALIES
# ============================================================================
print("\n" + "=" * 100)
print("3. PRICE ANOMALIES")
print("=" * 100)

price_data = derived['price_num'].dropna()
if len(price_data) > 0:
    print(f"\nPrice statistics:")
    print(f"  • Median: £{price_data.median():.0f}")
    print(f"  • Mean: £{price_data.mean():.0f}")
    print(f"  • Std Dev: £{price_data.std():.0f}")
    print(f"  • Min: £{price_data.min():.0f}")
    print(f"  • Max: £{price_data.max():.0f}")
    
    # Extremely low prices (suspiciously cheap)
    suspiciously_cheap = derived[derived['price_num'] < 50]
    print(f"\n  ⚠️  Suspiciously LOW (<£50): {len(suspiciously_cheap)} listings")
    if len(suspiciously_cheap) > 0:
        print(f"     Count: {len(suspiciously_cheap)} | Avg: £{suspiciously_cheap['price_num'].mean():.0f}")
        for _, row in suspiciously_cheap.head(3).iterrows():
            print(f"     • {row['platform']}: £{row['price_num']:.0f} - {row['breed']}")
    
    # Extremely high prices (suspiciously expensive)
    suspiciously_expensive = derived[derived['price_num'] > 5000]
    print(f"\n  ⚠️  Suspiciously HIGH (>£5,000): {len(suspiciously_expensive)} listings")
    if len(suspiciously_expensive) > 0:
        print(f"     Count: {len(suspiciously_expensive)} | Avg: £{suspiciously_expensive['price_num'].mean():.0f}")
        for _, row in suspiciously_expensive.head(3).iterrows():
            print(f"     • {row['platform']}: £{row['price_num']:.0f} - {row['breed']}")
    
    # Zero or missing price
    no_price = facts[facts['price'].isna() | (facts['price'] == '') | (facts['price'] == '0')]
    print(f"\n  ⚠️  Missing/zero price: {len(no_price)} listings ({len(no_price)/len(facts)*100:.1f}%)")

# ============================================================================
# 4. DATE ANOMALIES
# ============================================================================
print("\n" + "=" * 100)
print("4. DATE ANOMALIES")
print("=" * 100)

now = datetime.now()

# Check for future-dated listings
if 'published_at_ts' in derived.columns:
    try:
        ts_col = pd.to_datetime(derived['published_at_ts'], errors='coerce')
        future = derived[ts_col > now]
        print(f"\nFuture-dated listings (published after today): {len(future)}")
        if len(future) > 0:
            for idx, row in future.head(3).iterrows():
                print(f"  • {row['platform']}: {ts_col.iloc[idx]}")
    except:
        print(f"\nFuture-dated listings: Unable to parse timestamps")

# Check for very old listings (>2 years)
if 'published_at_ts' in derived.columns:
    try:
        ts_col = pd.to_datetime(derived['published_at_ts'], errors='coerce')
        two_years_ago = now - timedelta(days=730)
        ancient = derived[ts_col < two_years_ago]
        print(f"\nVery old listings (>2 years): {len(ancient)}")
        if len(ancient) > 0:
            for idx, row in ancient.head(3).iterrows():
                print(f"  • {row['platform']}: {ts_col.iloc[idx]}")
    except:
        print(f"Very old listings: Unable to parse timestamps")

# DOB anomalies
if 'date_of_birth' in facts.columns:
    dob_future = facts[pd.notna(facts['date_of_birth'])]
    print(f"\nDate of birth anomalies:")
    print(f"  • Records with DOB: {len(dob_future)}")
    # Would need parsing to check for impossible dates

# ============================================================================
# 5. AVAILABILITY/READINESS ANOMALIES
# ============================================================================
print("\n" + "=" * 100)
print("5. AVAILABILITY & READINESS ANOMALIES")
print("=" * 100)

print(f"\nReady-to-leave parse modes:")
for mode, count in derived['ready_to_leave_parse_mode'].value_counts().items():
    pct = (count / len(derived)) * 100
    print(f"  • {mode}: {count:,} ({pct:.1f}%)")

if 'age_days' in derived.columns:
    # Negative age is impossible
    negative_age = derived[derived['age_days'] < 0]
    print(f"\nNegative age_days (impossible): {len(negative_age)}")
    
    # Age too young to sell
    too_young = derived[derived['age_days'] < 42]  # Less than 6 weeks
    print(f"Suspiciously young (<6 weeks): {len(too_young)}")
    
    # Age too old for puppies
    too_old = derived[derived['age_days'] > 365]  # Over 1 year
    print(f"Over 1 year old (probably adult dogs, not puppies): {len(too_old)}")

# ============================================================================
# 6. AVAILABILITY COUNTS ANOMALIES
# ============================================================================
print("\n" + "=" * 100)
print("6. AVAILABILITY COUNTS ANOMALIES")
print("=" * 100)

if 'total_available' in facts.columns:
    total_avail = pd.to_numeric(facts['total_available'], errors='coerce')
    
    zero_available = (total_avail == 0).sum()
    missing_avail = total_avail.isna().sum()
    
    print(f"\nTotal available counts:")
    print(f"  • Zero available: {zero_available} ({zero_available/len(facts)*100:.1f}%)")
    print(f"  • Missing/unknown: {missing_avail} ({missing_avail/len(facts)*100:.1f}%)")
    print(f"  • With data: {(total_avail > 0).sum()} ({(total_avail > 0).sum()/len(facts)*100:.1f}%)")
    
    if (total_avail > 0).sum() > 0:
        print(f"  • Max available in single listing: {total_avail.max():.0f}")
        print(f"  • Listings claiming >20 puppies: {(total_avail > 20).sum()}")

# ============================================================================
# 7. MISSING CRITICAL DATA
# ============================================================================
print("\n" + "=" * 100)
print("7. MISSING CRITICAL DATA")
print("=" * 100)

critical_fields = ['url', 'breed', 'price', 'title', 'location', 'seller_name', 'published_at']
print(f"\nCritical field fill rates:")
for field in critical_fields:
    if field in facts.columns:
        filled = facts[field].notna().sum()
        pct = (filled / len(facts)) * 100
        status = "✓" if pct >= 95 else "⚠️" if pct >= 80 else "❌"
        print(f"  {status} {field.ljust(20)}: {filled:,}/{len(facts):,} ({pct:.1f}%)")

# ============================================================================
# 8. SELLER ANOMALIES
# ============================================================================
print("\n" + "=" * 100)
print("8. SELLER ANOMALIES")
print("=" * 100)

if 'seller_name' in facts.columns:
    # Count unique sellers
    unique_sellers = facts['seller_name'].nunique()
    print(f"\nUnique sellers: {unique_sellers:,}")
    
    # Sellers with most listings
    top_sellers = facts['seller_name'].value_counts().head(10)
    print(f"\nTop 10 sellers by listing count:")
    for seller, count in top_sellers.items():
        if pd.notna(seller) and seller != '':
            pct = (count / len(facts)) * 100
            print(f"  • {seller[:50].ljust(50)} - {count:,} listings ({pct:.1f}%)")

# Check for spam-like seller names
spam_sellers = facts[facts['seller_name'].isin(['test', 'spam', 'xxx', '123'])]
print(f"\nSuspicious seller names: {len(spam_sellers)}")

# ============================================================================
# 9. BREED QUALITY CHECK
# ============================================================================
print("\n" + "=" * 100)
print("9. BREED DATA QUALITY")
print("=" * 100)

if 'breed' in facts.columns:
    missing_breed = facts['breed'].isna().sum() + (facts['breed'] == '').sum()
    print(f"\nMissing breed: {missing_breed} ({missing_breed/len(facts)*100:.1f}%)")
    
    # Common breeds
    top_breeds = facts['breed'].value_counts().head(10)
    print(f"\nTop 10 breeds:")
    for breed, count in top_breeds.items():
        if pd.notna(breed) and breed != '':
            pct = (count / len(facts)) * 100
            print(f"  • {breed.ljust(30)}: {count:,} ({pct:.1f}%)")
    
    # Suspicious breed names
    suspicious = facts[facts['breed'].str.contains('test|spam|xxx|n/a|na|none', case=False, na=False)]
    print(f"\nSuspicious breed names: {len(suspicious)}")
    if len(suspicious) > 0:
        for breed in suspicious['breed'].unique()[:5]:
            count = len(suspicious[suspicious['breed'] == breed])
            print(f"  • {breed}: {count}")

# ============================================================================
# 10. SUMMARY & RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 100)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 100)

issues_found = {
    'duplicates': url_dupes_count,
    'non_dogs': len(suspicious_breeds),
    'price_anomalies': len(suspiciously_cheap) + len(suspiciously_expensive),
    'missing_breed': missing_breed,
}

total_issues = sum(issues_found.values())

print(f"\n⚠️  ISSUES FOUND: {total_issues}\n")
for issue, count in sorted(issues_found.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  • {issue.replace('_', ' ').title()}: {count}")

if total_issues == 0:
    print("  ✓ No major issues detected")

print(f"\n✓ ACTIONABLE ITEMS:\n")
if url_dupes_count > 0:
    print(f"  1. Remove {total_dup_urls - url_dupes_count} duplicate records (keep latest by platform)")
if len(suspicious_breeds) > 0:
    print(f"  2. Review {len(suspicious_breeds)} suspicious non-dog entries")
if len(suspiciously_cheap) > 0:
    print(f"  3. Flag {len(suspiciously_cheap)} suspiciously cheap listings (possible spam/errors)")
if len(suspiciously_expensive) > 0:
    print(f"  4. Review {len(suspiciously_expensive)} extremely expensive listings (possible errors)")
if missing_breed > len(facts) * 0.05:
    print(f"  5. Consider strategies for filling missing breed data")

print("\n" + "=" * 100)
