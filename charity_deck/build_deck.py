#!/usr/bin/env python3
"""
Build script for Charity deck presentation.
Renders index.html from Jinja2 template using canonical_metrics.json data.
"""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"
OUTPUT_FILE = SCRIPT_DIR / "index.html"
METRICS_FILE = PROJECT_ROOT / "canonical_metrics.json"

# Platform display names
PLATFORM_DISPLAY_NAMES = {
    "pets4homes": "Pets4Homes",
    "freeads": "FreeAds",
    "gumtree": "Gumtree",
    "preloved": "Preloved",
    "puppies": "Puppies.co.uk",
    "kennel_club": "Kennel Club",
    "petify": "Petify",
    "foreverpuppy": "ForeverPuppy",
    "champdogs": "Champdogs",
    "gundogs_direct": "Gundogs Direct",
}

# Short platform names for tight spaces
PLATFORM_SHORT_NAMES = {
    "pets4homes": "P4H",
    "freeads": "FreeAds",
    "gumtree": "Gumtree",
    "preloved": "Preloved",
    "puppies": "Puppies",
    "kennel_club": "KC",
    "petify": "Petify",
    "foreverpuppy": "ForeverPuppy",
    "champdogs": "Champdogs",
    "gundogs_direct": "Gundogs",
}


def format_k(value):
    """Format number with k suffix (e.g., 59000 -> 59k)"""
    if value is None:
        return "—"
    if value >= 1000:
        return f"{value / 1000:.0f}k"
    return str(int(value))


def format_comma(value):
    """Format number with comma separators (e.g., 19317 -> 19,317)"""
    if value is None:
        return "—"
    return f"{value:,}"


def format_pct(value):
    """Format as percentage (e.g., 94.43 -> 94%)"""
    if value is None:
        return "—"
    return f"{int(round(value))}%"


def format_price(value):
    """Format as GBP price (e.g., 3000 -> £3,000)"""
    if value is None:
        return "—"
    return f"£{value:,}"


def format_int(value):
    """Format as integer"""
    if value is None:
        return "—"
    return str(int(value))


def display_name(platform_key):
    """Get display name for platform"""
    return PLATFORM_DISPLAY_NAMES.get(platform_key, platform_key)


def short_name(platform_key):
    """Get short name for platform"""
    return PLATFORM_SHORT_NAMES.get(platform_key, platform_key)


def load_metrics():
    """Load canonical metrics from JSON file"""
    with open(METRICS_FILE, "r") as f:
        return json.load(f)


def compute_welfare_metrics(metrics):
    """Compute additional welfare-focused metrics from base data"""
    sellers = metrics.get("sellers", {})
    by_platform = sellers.get("by_platform", {})

    # Total high-volume sellers and licensed count
    total_hv = 0
    total_licensed = 0
    for key, data in by_platform.items():
        hv = data.get("high_volume", 0)
        licensed = data.get("license_sellers", 0)
        total_hv += hv
        total_licensed += licensed

    # Overall license rate
    license_rate = (total_licensed / total_hv * 100) if total_hv > 0 else 0
    unlicensed_hv = total_hv - total_licensed

    # Under 8 weeks totals
    eight_week = metrics.get("eight_week_regulation", {})
    total_under_8w = sum(p.get("total_under_8w", 0) for p in eight_week.values())
    total_protected = sum(p.get("has_future_date", 0) for p in eight_week.values())

    # Unlicensed breeders from top 10 (non-rescue)
    top_10 = sellers.get("top_10", [])
    unlicensed_breeders = [s for s in top_10 if not s.get("is_rescue") and not s.get("has_license")]

    return {
        "total_high_volume": total_hv,
        "total_licensed": total_licensed,
        "total_unlicensed": unlicensed_hv,
        "license_rate_pct": round(license_rate, 1),
        "unlicensed_rate_pct": round(100 - license_rate, 1),
        "total_under_8w": total_under_8w,
        "total_8w_protected": total_protected,
        "unlicensed_breeders": unlicensed_breeders[:5],
    }


def build_deck():
    """Build the deck HTML from template and metrics"""
    # Load metrics
    metrics = load_metrics()

    # Add display names to platforms
    for key, platform in metrics.get("platforms", {}).items():
        platform["display_name"] = display_name(key)
        platform["short_name"] = short_name(key)

    # Add display names to seller by_platform
    for key, seller_data in metrics.get("sellers", {}).get("by_platform", {}).items():
        seller_data["display_name"] = display_name(key)
        seller_data["short_name"] = short_name(key)

    # Add display names to freshness
    for key, freshness_data in metrics.get("freshness", {}).items():
        freshness_data["display_name"] = display_name(key)
        freshness_data["short_name"] = short_name(key)

    # Add display names to age_distribution
    for key, age_data in metrics.get("age_distribution", {}).items():
        age_data["display_name"] = display_name(key)
        age_data["short_name"] = short_name(key)

    # Add display names to eight_week_regulation
    for key, reg_data in metrics.get("eight_week_regulation", {}).items():
        reg_data["display_name"] = display_name(key)
        reg_data["short_name"] = short_name(key)

    # Compute welfare-specific metrics
    welfare = compute_welfare_metrics(metrics)
    metrics["welfare"] = welfare

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,  # HTML template, escaping handled manually
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Register custom filters
    env.filters["format_k"] = format_k
    env.filters["format_comma"] = format_comma
    env.filters["format_pct"] = format_pct
    env.filters["format_price"] = format_price
    env.filters["format_int"] = format_int
    env.filters["display_name"] = display_name
    env.filters["short_name"] = short_name

    # Load and render template
    template = env.get_template("index.html.j2")
    html = template.render(**metrics)

    # Write output
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print(f"Generated {OUTPUT_FILE}")
    print(f"  - {metrics['summary']['unique_puppies']:,} unique puppies")
    print(f"  - {len(metrics['platforms'])} platforms")
    print(f"  - {welfare['total_high_volume']} high-volume sellers")
    print(f"  - {welfare['license_rate_pct']}% licensed ({welfare['total_licensed']}/{welfare['total_high_volume']})")


if __name__ == "__main__":
    build_deck()
