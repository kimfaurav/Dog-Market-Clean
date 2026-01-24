#!/usr/bin/env python3
"""
Scraper QA - Validates scraper output before pipeline ingestion
Catches common issues: duplicate sellers, missing fields, suspicious patterns
"""

import json
import csv
import sys
from pathlib import Path
from collections import Counter

INPUT_DIR = Path(__file__).parent.parent / "Input" / "Raw CSVs"

# Minimum thresholds
MIN_FIELD_COVERAGE = {
    'price': 0.80,
    'location': 0.50,
    'seller_name': 0.50,
    'posted_date': 0.30,
}

# Max percentage for any single value (detects scraper bugs)
# These are field-specific - seller names should be diverse, breeds less so
MAX_SINGLE_VALUE_PCT = {
    'seller_name': 0.10,  # No single seller should be >10% of listings
    'location': 0.15,     # Location can have some clustering
    'breed': 0.50,        # Breed concentration is normal for niche platforms
}


def load_data(platform):
    """Load scraper output (JSON or CSV)"""
    json_path = INPUT_DIR / f"{platform}_data.json"
    csv_path = INPUT_DIR / f"{platform}_data.csv"

    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    elif csv_path.exists():
        with open(csv_path) as f:
            return list(csv.DictReader(f))
    else:
        raise FileNotFoundError(f"No data file found for {platform}")


def check_field_coverage(data, field):
    """Check what percentage of records have a non-empty value for field"""
    filled = sum(1 for row in data if row.get(field) and str(row[field]).strip())
    return filled / len(data) if data else 0


def check_value_distribution(data, field):
    """Check if any single value dominates (indicates scraper bug)"""
    values = [str(row.get(field, '')).strip() for row in data if row.get(field)]
    if not values:
        return None, 0

    counter = Counter(values)
    most_common_value, most_common_count = counter.most_common(1)[0]
    pct = most_common_count / len(values)
    return most_common_value, pct


def qa_platform(platform):
    """Run QA checks on a platform's scraper output"""
    print(f"\n{'='*60}")
    print(f"QA: {platform}")
    print(f"{'='*60}")

    try:
        data = load_data(platform)
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        return False

    print(f"  Records: {len(data)}")

    issues = []
    warnings = []

    # Check field coverage
    print(f"\n  Field Coverage:")
    for field, min_pct in MIN_FIELD_COVERAGE.items():
        coverage = check_field_coverage(data, field)
        status = "✓" if coverage >= min_pct else "✗"
        print(f"    {field}: {coverage*100:.0f}% {status}")
        if coverage < min_pct:
            issues.append(f"{field} coverage {coverage*100:.0f}% < {min_pct*100:.0f}% minimum")

    # Check for suspicious value distributions (scraper bugs)
    print(f"\n  Value Distribution (checking for scraper bugs):")
    for field in ['seller_name', 'location', 'breed']:
        top_value, top_pct = check_value_distribution(data, field)
        max_pct = MAX_SINGLE_VALUE_PCT.get(field, 0.20)
        if top_value:
            status = "✓" if top_pct <= max_pct else "⚠"
            print(f"    {field}: top value '{top_value[:40]}' = {top_pct*100:.1f}% {status}")
            if top_pct > max_pct:
                issues.append(f"{field} has suspicious concentration: '{top_value[:30]}' = {top_pct*100:.1f}% (max {max_pct*100:.0f}%)")

    # Check for unique sellers vs listings ratio
    sellers = set(str(row.get('seller_name', '')).strip() for row in data if row.get('seller_name'))
    if sellers:
        ratio = len(sellers) / len(data)
        print(f"\n  Seller Diversity:")
        print(f"    Unique sellers: {len(sellers)} ({ratio*100:.0f}% of listings)")
        if ratio < 0.3:
            warnings.append(f"Low seller diversity: only {len(sellers)} unique sellers for {len(data)} listings")

    # Summary
    print(f"\n  {'─'*50}")
    if issues:
        print(f"  ✗ FAILED - {len(issues)} issue(s):")
        for issue in issues:
            print(f"    • {issue}")
        return False
    elif warnings:
        print(f"  ⚠ PASSED with warnings:")
        for warning in warnings:
            print(f"    • {warning}")
        return True
    else:
        print(f"  ✓ PASSED")
        return True


def main():
    platforms = sys.argv[1:] if len(sys.argv) > 1 else ['gundogs_direct']

    print("SCRAPER QA VALIDATION")
    print("=" * 60)

    results = {}
    for platform in platforms:
        results[platform] = qa_platform(platform)

    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed > 0:
        print("\n  ⚠ Fix issues before running pipeline!")
        sys.exit(1)


if __name__ == "__main__":
    main()
