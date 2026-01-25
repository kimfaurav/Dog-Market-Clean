#!/usr/bin/env python3
"""
Build script for Gumtree deck presentation.
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
    print(f"  - {metrics['summary']['market_share_pct']}% market share")


if __name__ == "__main__":
    build_deck()
