#!/usr/bin/env python3
"""
Pipeline Step 2: Build Derived Views

Reads facts.csv and produces derived.csv with all parsing, heuristics, and flags.

This is where ALL derivations live:
- Timestamp parsing (*_ts columns)
- Numeric parsing (*_num columns)
- asof_ts anchor
- age_days calculation
- ready_to_leave parsing (platform-specific)
- is_ready_now / is_waiting_list flags

Output: output/views/derived.csv (single authoritative file)
"""

from pathlib import Path
import re
import pandas as pd
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
FACTS_PATH = REPO_ROOT / "output" / "facts" / "facts.csv"
OUTPUT_PATH = REPO_ROOT / "output" / "views" / "derived.csv"

# Ensure output directory exists
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Regex patterns for ready_to_leave parsing
NOW_RE = re.compile(r"^\s*now\s*$", re.IGNORECASE)
WEEKS_RE = re.compile(r"(?:in\s*)?(\d+)\s*week[s]?\b", re.IGNORECASE)
ORDINAL_RE = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)
MONTH_NAMES = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_RE = re.compile(rf"(\d{{1,2}})\s*(?:st|nd|rd|th)?\s*(?:of\s*)?({MONTH_NAMES})", re.IGNORECASE)


def parse_relative_date(text: str, anchor: pd.Timestamp) -> pd.Timestamp | None:
    """
    Parse relative date strings like '6 days ago', '2 weeks ago'.
    Returns absolute timestamp anchored to given anchor date.
    """
    if pd.isna(text) or not text:
        return None
    
    text = str(text).lower().strip()
    
    # Days ago
    m = re.search(r"(\d+)\s*day[s]?\s*ago", text)
    if m:
        days = int(m.group(1))
        return anchor - pd.Timedelta(days=days)
    
    # Weeks ago
    m = re.search(r"(\d+)\s*week[s]?\s*ago", text)
    if m:
        weeks = int(m.group(1))
        return anchor - pd.Timedelta(weeks=weeks)
    
    # Months ago
    m = re.search(r"(\d+)\s*month[s]?\s*ago", text)
    if m:
        months = int(m.group(1))
        return anchor - pd.Timedelta(days=months * 30)
    
    return None


def to_datetime_safe(series: pd.Series) -> pd.Series:
    """
    Parse datetime with coercion, UTC-aware.
    Handles multiple formats by falling back to individual parsing.
    """
    # First try standard parsing
    result = pd.to_datetime(series, errors="coerce", utc=True)
    
    # For any that failed, try individual parsing (handles UK date formats)
    failed_mask = result.isna() & series.notna() & (series != "")
    if failed_mask.any():
        for idx in series.index[failed_mask]:
            val = series.loc[idx]
            try:
                # dateutil handles most formats including "18th December 2025"
                from dateutil import parser as dateutil_parser
                parsed = dateutil_parser.parse(str(val))
                result.loc[idx] = pd.Timestamp(parsed, tz="UTC")
            except:
                pass
    
    return result


def add_typed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add parsed timestamp and numeric columns."""
    out = df.copy()
    
    # Pipeline run timestamp (UTC) — stable anchor for relative strings
    out["asof_ts"] = datetime.now(timezone.utc)
    
    # Datetime columns (mechanical parsing)
    dt_fields = [
        "created_at", "published_at", "refreshed_at",
        "date_of_birth", "ready_to_leave",
        "member_since", "last_active", "license_valid",
    ]
    for col in dt_fields:
        if col in out.columns:
            out[f"{col}_ts"] = to_datetime_safe(out[col])
    
    # Numeric columns (mechanical parsing)
    num_fields = [
        "price", "males_available", "females_available", "total_available",
        "response_hours", "reviews", "rating", "views_count",
        "active_listings", "active_pets",
    ]
    for col in num_fields:
        if col in out.columns:
            # Strip currency symbols and commas for price
            if col == "price":
                cleaned = out[col].astype(str).str.replace(r"[£$,]", "", regex=True)
                out[f"{col}_num"] = pd.to_numeric(cleaned, errors="coerce")
            else:
                out[f"{col}_num"] = pd.to_numeric(out[col], errors="coerce")
    
    return out


def add_age_days(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate age in days from date_of_birth and asof_ts."""
    out = df.copy()
    
    if "date_of_birth_ts" in out.columns:
        out["age_days"] = (out["asof_ts"] - out["date_of_birth_ts"]).dt.days
    else:
        out["age_days"] = pd.NA
    
    return out


def parse_ready_to_leave_pets4homes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pets4Homes: ready_to_leave is typically a proper date string.
    High confidence - direct date parsing.
    """
    out = df.copy()
    mask = out["platform"] == "pets4homes"
    
    if not mask.any():
        return out
    
    # ready_to_leave_ts already parsed in add_typed_columns
    # Calculate days until ready
    out.loc[mask, "ready_to_leave_parsed_ts"] = out.loc[mask, "ready_to_leave_ts"]
    out.loc[mask, "ready_to_leave_parse_mode"] = out.loc[mask, "ready_to_leave_ts"].apply(
        lambda x: "date" if pd.notna(x) else "unknown"
    )
    
    return out


def parse_ready_to_leave_gumtree(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gumtree: Strings like 'Now', 'in 2 weeks'.
    High confidence for these patterns.
    """
    out = df.copy()
    mask = out["platform"] == "gumtree"
    
    if not mask.any():
        return out
    
    g = out.loc[mask].copy()
    rtl = g["ready_to_leave"].astype("string").fillna("")
    
    # Anchor: use published_at_ts if available, else asof_ts
    anchor = g["published_at_ts"].where(g["published_at_ts"].notna(), g["asof_ts"])
    
    # Initialize columns with proper types
    g["ready_to_leave_parsed_ts"] = pd.Series(pd.NaT, index=g.index, dtype="datetime64[ns, UTC]")
    g["ready_to_leave_parse_mode"] = "unknown"
    
    # "Now" pattern
    is_now = rtl.str.match(NOW_RE)
    g.loc[is_now, "ready_to_leave_parsed_ts"] = anchor[is_now]
    g.loc[is_now, "ready_to_leave_parse_mode"] = "now"
    
    # "in N weeks" pattern
    extracted = rtl.str.extract(WEEKS_RE)
    has_weeks = extracted[0].notna()
    weeks = pd.to_numeric(extracted[0], errors="coerce")
    days = weeks * 7
    
    g.loc[has_weeks, "ready_to_leave_parsed_ts"] = anchor[has_weeks] + pd.to_timedelta(days[has_weeks], unit="D")
    g.loc[has_weeks, "ready_to_leave_parse_mode"] = "in_weeks"
    
    # Write back
    out.loc[mask, "ready_to_leave_parsed_ts"] = g["ready_to_leave_parsed_ts"]
    out.loc[mask, "ready_to_leave_parse_mode"] = g["ready_to_leave_parse_mode"]
    
    return out


def parse_ready_to_leave_freeads(df: pd.DataFrame) -> pd.DataFrame:
    """
    Freeads: Mixed formats - 'Now', '8 weeks', '7th February'.
    
    For date strings like '7th February':
    - Anchor to asof_ts year
    - Choose nearest future date
    - If >180 days ahead, treat as unknown
    """
    out = df.copy()
    mask = out["platform"] == "freeads"
    
    if not mask.any():
        return out
    
    f = out.loc[mask].copy()
    rtl = f["ready_to_leave"].astype("string").fillna("").str.strip()
    
    # Anchor: use published_at_ts if available, else asof_ts
    # Note: Freeads published_at may be relative text like "6 days ago"
    # Try to parse it first
    anchor = f["asof_ts"].copy()
    for idx in f.index:
        pub = f.loc[idx, "published_at"]
        pub_ts = f.loc[idx, "published_at_ts"]
        if pd.notna(pub_ts):
            anchor.loc[idx] = pub_ts
        elif pd.notna(pub):
            # Try parsing relative date
            parsed = parse_relative_date(pub, f.loc[idx, "asof_ts"])
            if parsed:
                anchor.loc[idx] = parsed
    
    # Initialize columns with proper types
    f["ready_to_leave_parsed_ts"] = pd.Series(pd.NaT, index=f.index, dtype="datetime64[ns, UTC]")
    f["ready_to_leave_parse_mode"] = "unknown"
    
    # "Now" pattern
    is_now = rtl.str.match(NOW_RE)
    f.loc[is_now, "ready_to_leave_parsed_ts"] = anchor[is_now]
    f.loc[is_now, "ready_to_leave_parse_mode"] = "now"
    
    # "N weeks" pattern (with or without "in")
    wk_extract = rtl.str.extract(WEEKS_RE)
    has_weeks = wk_extract[0].notna() & ~is_now
    weeks = pd.to_numeric(wk_extract[0], errors="coerce")
    days = weeks * 7
    
    f.loc[has_weeks, "ready_to_leave_parsed_ts"] = anchor[has_weeks] + pd.to_timedelta(days[has_weeks], unit="D")
    f.loc[has_weeks, "ready_to_leave_parse_mode"] = "in_weeks"
    
    # Date strings like "7th February", "22nd November"
    # Normalize: remove ordinal suffixes, 'of' word
    normalized = (rtl
        .str.replace(ORDINAL_RE, r"\1", regex=True)
        .str.replace(r"\bof\b", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip())
    
    # Extract day and month
    date_match = normalized.str.extract(DATE_RE)
    has_date = date_match[0].notna() & ~is_now & ~has_weeks
    
    # Build full date string with anchor year
    for idx in f.index[has_date]:
        day = date_match.loc[idx, 0]
        month = date_match.loc[idx, 1]
        anchor_year = anchor.loc[idx].year
        
        # Try parsing with anchor year
        date_str = f"{day} {month} {anchor_year}"
        try:
            parsed = pd.to_datetime(date_str, utc=True)
            
            # If parsed date is in the past by >180 days, bump to next year
            delta = (parsed - anchor.loc[idx]).days
            if delta < -180:
                parsed = parsed + pd.DateOffset(years=1)
            
            # If >180 days in future, mark as unknown (suspicious)
            delta_future = (parsed - anchor.loc[idx]).days
            if delta_future > 180:
                f.loc[idx, "ready_to_leave_parse_mode"] = "date_suspicious"
            else:
                f.loc[idx, "ready_to_leave_parsed_ts"] = parsed
                f.loc[idx, "ready_to_leave_parse_mode"] = "date_anchored"
        except:
            pass
    
    # Write back
    out.loc[mask, "ready_to_leave_parsed_ts"] = f["ready_to_leave_parsed_ts"]
    out.loc[mask, "ready_to_leave_parse_mode"] = f["ready_to_leave_parse_mode"]
    
    return out


def parse_ready_to_leave_other(df: pd.DataFrame) -> pd.DataFrame:
    """
    Other platforms: Try direct date parsing, else mark unknown.
    
    For platforms with date_of_birth but no ready_to_leave,
    estimate ready_to_leave as date_of_birth + 8 weeks (typical weaning age).
    """
    out = df.copy()
    other_platforms = ["preloved", "kennel_club", "foreverpuppy", "petify", "puppies", "champdogs"]
    mask = out["platform"].isin(other_platforms)
    
    if not mask.any():
        return out
    
    # For rows where ready_to_leave_parsed_ts isn't set yet
    unset = mask & out["ready_to_leave_parsed_ts"].isna()
    
    for idx in out.index[unset]:
        rtl = out.loc[idx, "ready_to_leave"]
        platform = out.loc[idx, "platform"]
        
        if pd.isna(rtl) or str(rtl).strip() == "":
            # Check if we have date_of_birth as fallback
            dob_ts = out.loc[idx, "date_of_birth_ts"]
            if pd.notna(dob_ts):
                # Estimate ready_to_leave as DOB + 8 weeks
                estimated = dob_ts + pd.Timedelta(weeks=8)
                out.loc[idx, "ready_to_leave_parsed_ts"] = estimated
                out.loc[idx, "ready_to_leave_parse_mode"] = "dob_plus_8wks"
            else:
                out.loc[idx, "ready_to_leave_parse_mode"] = "missing"
            continue
        
        rtl_str = str(rtl).lower().strip()
        
        # Check for "now"
        if NOW_RE.match(rtl_str):
            out.loc[idx, "ready_to_leave_parsed_ts"] = out.loc[idx, "asof_ts"]
            out.loc[idx, "ready_to_leave_parse_mode"] = "now"
            continue
        
        # Try direct date parsing
        ts = out.loc[idx, "ready_to_leave_ts"]
        if pd.notna(ts):
            out.loc[idx, "ready_to_leave_parsed_ts"] = ts
            out.loc[idx, "ready_to_leave_parse_mode"] = "date"
        else:
            # Fallback to DOB + 8 weeks if available
            dob_ts = out.loc[idx, "date_of_birth_ts"]
            if pd.notna(dob_ts):
                estimated = dob_ts + pd.Timedelta(weeks=8)
                out.loc[idx, "ready_to_leave_parsed_ts"] = estimated
                out.loc[idx, "ready_to_leave_parse_mode"] = "dob_plus_8wks"
            else:
                out.loc[idx, "ready_to_leave_parse_mode"] = "unknown"
    
    return out


def validate_puppy_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate total_available_num to catch parsing errors.
    
    Suspicious patterns:
    - Values >20 (unrealistic for single litter)
    - Values 1800-2099 (parsing prices or years)
    - Values in common year range (2000-2099)
    
    Action: Flag suspicious values with new column 'total_available_flag'
    and set total_available_num to NULL for investigation.
    """
    out = df.copy()
    
    if "total_available_num" not in out.columns:
        return out
    
    out["total_available_flag"] = "ok"
    
    # Mark suspicious values
    mask_over_20 = (out["total_available_num"].notna()) & (out["total_available_num"] > 20)
    mask_year_range = (out["total_available_num"].notna()) & (out["total_available_num"] >= 1800) & (out["total_available_num"] <= 2099)
    mask_price_like = (out["total_available_num"].notna()) & (out["total_available_num"] > 500)
    
    # Combine suspicious masks
    suspicious = mask_over_20 | mask_year_range | mask_price_like
    
    out.loc[suspicious, "total_available_flag"] = "suspicious_over_20_or_year"
    
    # For Freeads specifically (known bad data), be more aggressive
    freeads_mask = (out["platform"] == "freeads") & (out["total_available_num"].notna()) & (out["total_available_num"] > 20)
    out.loc[freeads_mask, "total_available_flag"] = "suspicious_freeads_outlier"
    
    # Nullify suspicious values
    out.loc[suspicious, "total_available_num"] = None

    # Recalculate total from males+females if available
    mask_recalc = (out["total_available_num"].isna()) & (out["males_available_num"].notna()) & (out["females_available_num"].notna())
    out.loc[mask_recalc, "total_available_num"] = out.loc[mask_recalc, "males_available_num"] + out.loc[mask_recalc, "females_available_num"]

    # Clamp any remaining totals over 12 to 12
    mask_clamp = (out["total_available_num"].notna()) & (out["total_available_num"] > 12)
    out.loc[mask_clamp & (out["total_available_flag"] == "ok"), "total_available_flag"] = "clamped_over_12"
    out.loc[mask_clamp, "total_available_num"] = 12
    
    return out


def add_availability_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add final availability flags based on parsed ready_to_leave.
    
    - days_until_ready: (ready_to_leave_parsed_ts - asof_ts).days
    - is_ready_now: days_until_ready <= 0
    - is_waiting_list: days_until_ready > 0
    - availability_known: ready_to_leave_parse_mode not in ['unknown', 'missing', 'date_suspicious']
    """
    out = df.copy()
    
    # Ensure datetime columns are proper datetime types
    out["ready_to_leave_parsed_ts"] = pd.to_datetime(out["ready_to_leave_parsed_ts"], errors="coerce", utc=True)
    out["asof_ts"] = pd.to_datetime(out["asof_ts"], errors="coerce", utc=True)
    
    # Days until ready
    out["days_until_ready"] = (out["ready_to_leave_parsed_ts"] - out["asof_ts"]).dt.days
    
    # Flags
    out["is_ready_now"] = out["days_until_ready"].notna() & (out["days_until_ready"] <= 0)
    out["is_waiting_list"] = out["days_until_ready"].notna() & (out["days_until_ready"] > 0)
    out["availability_known"] = ~out["ready_to_leave_parse_mode"].isin(["unknown", "missing", "date_suspicious"])
    
    return out


def main():
    print("=" * 60)
    print("Pipeline Step 2: Build Derived Views")
    print("=" * 60)
    
    if not FACTS_PATH.exists():
        raise FileNotFoundError(f"Facts file not found: {FACTS_PATH}\nRun pipeline_01_build_facts.py first.")
    
    df = pd.read_csv(FACTS_PATH, dtype=str, keep_default_na=True, low_memory=False)
    print(f"Loaded facts: {len(df)} rows")
    
    # Step 1: Add typed columns (timestamps, numerics)
    print("\nAdding typed columns...")
    df = add_typed_columns(df)
        # Step 1b: Validate puppy counts (catch parsing errors)
    print("Validating puppy counts...")
    df = validate_puppy_counts(df)
        # Step 2: Add age_days
    print("Calculating age_days...")
    df = add_age_days(df)
    
    # Step 3: Parse ready_to_leave (platform-specific)
    print("Parsing ready_to_leave...")
    
    # Initialize columns with proper types
    df["ready_to_leave_parsed_ts"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    df["ready_to_leave_parse_mode"] = "unknown"
    
    df = parse_ready_to_leave_pets4homes(df)
    df = parse_ready_to_leave_gumtree(df)
    df = parse_ready_to_leave_freeads(df)
    df = parse_ready_to_leave_other(df)
    
    # Step 4: Add availability flags
    print("Adding availability flags...")
    df = add_availability_flags(df)
    
    # Write output
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "=" * 60)
    print(f"Total rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {OUTPUT_PATH}")
    
    # Summary stats
    print("\n=== Puppy Count Validation ===")
    if "total_available_flag" in df.columns:
        print(df["total_available_flag"].value_counts(dropna=False).to_string())
        flagged = (df["total_available_flag"] != "ok").sum()
        print(f"Total flagged as suspicious: {flagged} listings")
    
    print("\n=== Parse Mode Distribution ===")
    print(df["ready_to_leave_parse_mode"].value_counts(dropna=False).to_string())
    
    print("\n=== Availability by Platform ===")
    summary = df.groupby("platform").agg({
        "availability_known": "mean",
        "is_ready_now": "mean",
        "is_waiting_list": "mean",
    }).round(3)
    summary.columns = ["pct_availability_known", "pct_ready_now", "pct_waiting_list"]
    print(summary.to_string())


if __name__ == "__main__":
    main()
