#!/usr/bin/env python3
"""
Pipeline Step 1: Build Facts Table

Reads raw CSVs from Input/Raw CSVs/ and produces a single facts table
conforming strictly to schema/pets4homes_master_schema.csv + platform column.

No derivations, no heuristics - just field mapping.

Output: output/facts/facts.csv (single authoritative file, no timestamps)
"""

from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "Input" / "Raw CSVs"
SCHEMA_PATH = REPO_ROOT / "schema" / "pets4homes_master_schema.csv"
OUTPUT_PATH = REPO_ROOT / "output" / "facts" / "facts.csv"

# Ensure output directory exists
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_schema() -> list[str]:
    """Load schema field names from master schema CSV."""
    df = pd.read_csv(SCHEMA_PATH)
    fields = df['field_name'].str.strip().tolist()
    return fields


# Platform-specific file patterns and column mappings
# Key: platform name
# Value: dict with 'file_pattern' and 'mapping' (raw_col -> schema_col)
PLATFORM_CONFIG = {
    "pets4homes": {
        "file_pattern": "pets4homes_v7_complete*.csv",
        "mapping": {
            "url": "url",
            "created_at": "created_at",
            "published_at": "published_at",
            "refreshed_at": "refreshed_at",
            "title": "title",
            "breed": "breed",
            "date_of_birth": "date_of_birth",
            "ready_to_leave": "ready_to_leave",
            "males_available": "males_available",
            "females_available": "females_available",
            "total_available": "total_available",
            "price": "price",
            "location": "location",
            "seller_id": "seller_id",
            "seller_name": "seller_name",
            "company_name": "company_name",
            "user_type": "user_type",
            "is_breeder": "is_breeder",
            "license_num": "license_num",
            "license_auth": "license_auth",
            "license_status": "license_status",
            "license_valid": "license_valid",
            "kc_license": "kc_license",
            "member_since": "member_since",
            "last_active": "last_active",
            "response_hours": "response_hours",
            "reviews": "reviews",
            "rating": "rating",
            "views_count": "views_count",
            "active_listings": "active_listings",
            "active_pets": "active_pets",
        }
    },
    "gumtree": {
        "file_pattern": "gumtree_final*.csv",
        "mapping": {
            "url": "url",
            "ad_id": "ad_id",
            "posted": "published_at",
            "title": "title",
            "breed": "breed",
            "sex": "sex",
            "age_detail": "age",
            "ready_to_leave": "ready_to_leave",
            "price": "price",
            "location": "location",
            "seller_name": "seller_name",
            "microchipped": "microchipped",
            "vaccinated": "vaccinated",
            "kc_registered": "kc_registered",
            "health_checked": "health_checked",
            "neutered": "wormed",
            "deflead": "flea_treated",
            "description": "title",  # Use as secondary title source
        }
    },
    "freeads": {
        "file_pattern": "freeads_enriched_COMPLETE*.csv",
        "mapping": {
            "url": "url",
            "ad_id": "ad_id",
            "date_posted": "published_at",
            "title": "title",
            "breed": "breed",
            "sex": "sex",
            "color": "color",
            "age": "age",
            "puppy_age": "age",
            "ready_date": "ready_to_leave",
            "price": "price",
            "location": "location",
            "seller_name": "seller_name",
            "males_available": "males_available",
            "females_available": "females_available",
            "litter_size": "total_available",
            "kc_registered": "kc_registered",
            "microchipped": "microchipped",
            "vaccinated": "vaccinated",
            "wormed": "wormed",
            "flea_treated": "flea_treated",
            "vet_checked": "vet_checked",
            "health_checked": "health_checked",
            "pedigree": "pedigree",
            "dna_tested_parents": "dna_tested",
            "champion_bloodline": "champion_bloodline",
            "parents_visible": "pedigree",  # Secondary indicator
            "home_reared": "home_reared",
            "family_reared": "family_reared",
            "puppy_contract": "puppy_contract",
            "insurance": "insurance_available",
            "delivery_available": "delivery_available",
        }
    },
    "preloved": {
        "file_pattern": "preloved_enriched*.csv",
        "mapping": {
            "url": "url",
            "created": "published_at",
            "title": "title",
            "breed": "breed",
            "sex": "sex",
            "age": "age",
            "ready_to_leave": "ready_to_leave",
            "price": "price",
            "location": "location",
            "seller_name": "seller_name",
            "seller_type": "user_type",
            "member_since": "member_since",
            "views": "views_count",
            "kc_registered": "kc_registered",
            "microchipped": "microchipped",
            "neutered": "wormed",
            "vaccinations": "vaccinated",
            "health_checks": "health_checked",
        }
    },
    "kennel_club": {
        "file_pattern": "kc_data_PERFECT*.csv",
        "mapping": {
            "url": "url",
            "breed": "breed",
            "puppy_name": "title",
            "date_of_birth": "date_of_birth",
            "born": "ready_to_leave",
            "sex": "sex",
            "colour": "color",
            "price": "price",
            "location": "location",
            "county": "location",  # Secondary location
            "breeder_name": "seller_name",
            "phone": "seller_id",  # Store phone as seller_id if needed
            "license_number": "license_num",
            "council": "license_auth",
            "sire": "sire",
            "dam": "dam",
            "sire_health_tested": "sire_health_tested",
            "dam_health_tested": "dam_health_tested",
        }
    },
    "foreverpuppy": {
        "file_pattern": "foreverpuppy_FINAL*.csv",
        "mapping": {
            "url": "url",
            "ad_id": "ad_id",
            "created": "published_at",
            "title": "title",
            "breed": "breed",
            "age": "age",
            "ready_to_leave": "ready_to_leave",
            "price": "price",
            "location": "location",
            "seller_name": "seller_name",
            "seller_type": "user_type",
            "boys": "males_available",
            "girls": "females_available",
            "litter_size": "total_available",
            "kc_registered": "kc_registered",
            "microchipped": "microchipped",
            "vaccinated": "vaccinated",
            "available": "total_available",  # Secondary
        }
    },
    "petify": {
        "file_pattern": "petify_data_clean*.csv",
        "mapping": {
            "url": "url",
            "id": "ad_id",
            "title": "title",
            "breed": "breed",
            "ready_to_leave": "ready_to_leave",
            "price": "price",
            "location": "location",
            "seller_type": "user_type",
            "member_since": "member_since",
            "males_available": "males_available",
            "females_available": "females_available",
            "views": "views_count",
            "kc_registered": "kc_registered",
            "microchipped": "microchipped",
            "vaccinated": "vaccinated",
            "id_verified": "breeder_verified",
        }
    },
    "puppies": {
        "file_pattern": "puppies_final*.csv",
        "mapping": {
            "url": "url",
            "ad_reference": "ad_id",
            "posted_date": "published_at",
            "title": "title",
            "breed": "breed",
            "ready_to_leave": "ready_to_leave",
            "date_of_birth": "date_of_birth",
            "price": "price",
            "location": "location",
            "seller_name": "seller_name",
            "seller_type": "user_type",
            "member_since": "member_since",
            "males_available": "males_available",
            "females_available": "females_available",
            "puppies_available": "total_available",
            "health_tested": "health_tested",
            "vet_checked": "vet_checked",
            "wormed": "wormed",
            "flea_treated": "flea_treated",
            "sire_info": "sire",
            "dam_info": "dam",
        }
    },
    "champdogs": {
        "file_pattern": "champdogs_complete*.csv",
        "mapping": {
            "url": "url",
            "listing_id": "ad_id",
            "date_available": "ready_to_leave",
            "date_born": "date_of_birth",
            "breed": "breed",
            "price": "price",
            "location": "location",
            "county": "location",  # Secondary location
            "breeder_name": "seller_name",
            "breeder_url": "seller_id",
            "kennel_name": "company_name",
            "males_available": "males_available",
            "females_available": "females_available",
            "puppies_available": "total_available",
            "sire_name": "sire",
            "dam_name": "dam",
            "health_tested": "health_tested",
            "health_tests": "health_checked",
            "five_star_breeder": "five_star_breeder",
            "assured_breeder": "assured_breeder",
            "licensed_breeder": "licensed_breeder",
            "microchipped": "microchipped",
            "vaccinated": "vaccinated",
            "wormed": "wormed",
            "vet_checked": "vet_checked",
        }
    },
}


def load_platform_data(platform: str, config: dict) -> pd.DataFrame:
    """Load raw CSV for a platform and map columns to schema."""
    pattern = config["file_pattern"]
    files = list(RAW_DIR.glob(pattern))
    
    if not files:
        print(f"  WARNING: No files found for {platform} with pattern {pattern}")
        return pd.DataFrame()
    
    # Use most recent if multiple files
    file_path = sorted(files)[-1]
    print(f"  Loading: {file_path.name}")
    
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False, low_memory=False)
    print(f"    Raw rows: {len(df)}")
    
    return df


def map_to_schema(df: pd.DataFrame, platform: str, mapping: dict, schema_fields: list[str]) -> pd.DataFrame:
    """Map raw DataFrame columns to schema columns."""
    if df.empty:
        return pd.DataFrame(columns=["platform"] + schema_fields)
    
    # Build result DataFrame
    result = pd.DataFrame(index=df.index)
    result["platform"] = platform
    
    # Reverse mapping: schema_col -> raw_col
    reverse_map = {v: k for k, v in mapping.items()}
    
    for schema_col in schema_fields:
        if schema_col in reverse_map and reverse_map[schema_col] in df.columns:
            raw_col = reverse_map[schema_col]
            result[schema_col] = df[raw_col].replace("", pd.NA)
        else:
            result[schema_col] = pd.NA
    
    return result


def main():
    print("=" * 60)
    print("Pipeline Step 1: Build Facts Table")
    print("=" * 60)
    
    schema_fields = load_schema()
    print(f"Schema fields: {len(schema_fields)}")
    
    all_facts = []
    
    for platform, config in PLATFORM_CONFIG.items():
        print(f"\n[{platform}]")
        df = load_platform_data(platform, config)
        
        if not df.empty:
            facts = map_to_schema(df, platform, config["mapping"], schema_fields)
            all_facts.append(facts)
            print(f"    Mapped rows: {len(facts)}")
    
    # Combine all platforms
    print("\n" + "=" * 60)
    combined = pd.concat(all_facts, ignore_index=True)
    
    # Ensure column order: platform first, then schema fields
    combined = combined[["platform"] + schema_fields]
    
    # Write output
    combined.to_csv(OUTPUT_PATH, index=False)
    
    print(f"Total rows: {len(combined)}")
    print(f"Columns: {len(combined.columns)}")
    print(f"Output: {OUTPUT_PATH}")
    
    # Platform breakdown
    print("\nPlatform breakdown:")
    print(combined["platform"].value_counts().to_string())
    
    # Coverage stats for key fields
    print("\nKey field coverage:")
    for col in ["url", "breed", "price", "ready_to_leave", "date_of_birth", "published_at"]:
        if col in combined.columns:
            coverage = combined[col].notna().mean() * 100
            print(f"  {col}: {coverage:.1f}%")


if __name__ == "__main__":
    main()
