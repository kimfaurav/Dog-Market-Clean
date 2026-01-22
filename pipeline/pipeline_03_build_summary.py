#!/usr/bin/env python3
"""
Pipeline Step 3: Build Platform Supply Summary

Reads derived.csv and produces platform_supply_summary.csv.

This is the final analytical output showing:
- Total listings per platform
- Availability coverage and breakdown
- Price and age statistics
- Confidence notes per platform

Output: output/views/platform_supply_summary.csv (single authoritative file)
"""

from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVED_PATH = REPO_ROOT / "output" / "views" / "derived.csv"
OUTPUT_PATH = REPO_ROOT / "output" / "views" / "platform_supply_summary.csv"

# Platform-specific confidence notes
CONFIDENCE_NOTES = {
    "pets4homes": "High - structured date fields, ~100% coverage",
    "gumtree": "High - 'Now' and 'in N weeks' patterns reliably parsed",
    "freeads": "Medium - mixed formats; date strings anchored to asof_ts with ±180 day window",
    "preloved": "Low - limited ready_to_leave data; DOB+8wks fallback where available",
    "kennel_club": "Medium - DOB available; estimated ready_to_leave = DOB + 8 weeks",
    "foreverpuppy": "Low - limited ready_to_leave data",
    "petify": "Low - limited ready_to_leave data",
    "puppies": "Low - limited ready_to_leave data; DOB+8wks fallback where available",
    "champdogs": "Medium - DOB available; estimated ready_to_leave = DOB + 8 weeks",
}


def main():
    print("=" * 60)
    print("Pipeline Step 3: Build Platform Supply Summary")
    print("=" * 60)
    
    if not DERIVED_PATH.exists():
        raise FileNotFoundError(f"Derived file not found: {DERIVED_PATH}\nRun pipeline_02_build_derived.py first.")
    
    df = pd.read_csv(DERIVED_PATH, low_memory=False)
    print(f"Loaded derived: {len(df)} rows")
    
    # Ensure boolean columns are boolean
    for col in ["availability_known", "is_ready_now", "is_waiting_list"]:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    
    # Ensure numeric columns
    for col in ["price_num", "age_days", "days_until_ready"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Group by platform
    summary_rows = []
    
    for platform in sorted(df["platform"].unique()):
        p = df[df["platform"] == platform]
        n = len(p)
        
        # Availability metrics
        availability_known_pct = p["availability_known"].mean() if "availability_known" in p.columns else 0
        ready_now_count = p["is_ready_now"].sum() if "is_ready_now" in p.columns else 0
        waiting_list_count = p["is_waiting_list"].sum() if "is_waiting_list" in p.columns else 0
        unknown_count = n - ready_now_count - waiting_list_count
        
        pct_ready_now = ready_now_count / n if n > 0 else 0
        pct_waiting_list = waiting_list_count / n if n > 0 else 0
        pct_unknown = unknown_count / n if n > 0 else 0
        
        # Price metrics
        price_coverage_pct = p["price_num"].notna().mean() if "price_num" in p.columns else 0
        median_price = p["price_num"].median() if "price_num" in p.columns else np.nan
        
        # Age metrics
        age_coverage_pct = p["age_days"].notna().mean() if "age_days" in p.columns else 0
        median_age_days = p["age_days"].median() if "age_days" in p.columns else np.nan
        
        # Parse mode breakdown
        parse_modes = p["ready_to_leave_parse_mode"].value_counts(dropna=False).to_dict() if "ready_to_leave_parse_mode" in p.columns else {}
        
        summary_rows.append({
            "platform": platform,
            "total_listings": n,
            "availability_known_pct": round(availability_known_pct, 3),
            "ready_now_count": int(ready_now_count),
            "waiting_list_count": int(waiting_list_count),
            "unknown_count": int(unknown_count),
            "pct_ready_now": round(pct_ready_now, 3),
            "pct_waiting_list": round(pct_waiting_list, 3),
            "pct_unknown": round(pct_unknown, 3),
            "price_coverage_pct": round(price_coverage_pct, 3),
            "median_price": round(median_price, 0) if pd.notna(median_price) else None,
            "age_coverage_pct": round(age_coverage_pct, 3),
            "median_age_days": round(median_age_days, 0) if pd.notna(median_age_days) else None,
            "confidence_note": CONFIDENCE_NOTES.get(platform, "Unknown"),
        })
    
    summary_df = pd.DataFrame(summary_rows)
    
    # Sort by total_listings descending
    summary_df = summary_df.sort_values("total_listings", ascending=False)
    
    # Write output
    summary_df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "=" * 60)
    print(f"Output: {OUTPUT_PATH}")
    print("\n=== Platform Supply Summary ===")
    
    # Display key columns
    display_cols = ["platform", "total_listings", "availability_known_pct", 
                   "pct_ready_now", "pct_waiting_list", "confidence_note"]
    print(summary_df[display_cols].to_string(index=False))
    
    # Total across all platforms
    print("\n=== Totals ===")
    total_listings = summary_df["total_listings"].sum()
    total_ready_now = summary_df["ready_now_count"].sum()
    total_waiting_list = summary_df["waiting_list_count"].sum()
    total_unknown = summary_df["unknown_count"].sum()
    
    print(f"Total listings: {total_listings:,}")
    print(f"Ready now: {total_ready_now:,} ({total_ready_now/total_listings*100:.1f}%)")
    print(f"Waiting list: {total_waiting_list:,} ({total_waiting_list/total_listings*100:.1f}%)")
    print(f"Unknown: {total_unknown:,} ({total_unknown/total_listings*100:.1f}%)")


if __name__ == "__main__":
    main()
