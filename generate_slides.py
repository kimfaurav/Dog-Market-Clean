#!/usr/bin/env python3
"""
generate_slides.py - Inject canonical metrics into HTML slides

Reads canonical_metrics.json and updates uk_dog_market_slide.html with
current metric values, preserving HTML structure and styling.
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
METRICS_PATH = SCRIPT_DIR / "canonical_metrics.json"
HTML_PATH = SCRIPT_DIR / "uk_dog_market_slide.html"


def load_metrics(path: Path) -> dict:
    """Load metrics from JSON file."""
    with open(path) as f:
        return json.load(f)


def load_html(path: Path) -> str:
    """Load HTML template."""
    with open(path) as f:
        return f.read()


def save_html(path: Path, content: str) -> None:
    """Save updated HTML."""
    with open(path, "w") as f:
        f.write(content)


# =============================================================================
# Formatting helpers
# =============================================================================

def fmt_k(value: float) -> str:
    """Format number as Xk (thousands), e.g., 44087 -> '44k'."""
    return f"{round(value/1000)}k"


def fmt_comma(value: int) -> str:
    """Format number with commas, e.g., 19021 -> '19,021'."""
    return f"{value:,}"


def fmt_pct(value: float, decimals: int = 0) -> str:
    """Format as percentage string, e.g., 68.04 -> '68%'."""
    if decimals == 0:
        return f"{round(value)}%"
    return f"{value:.{decimals}f}%"


def fmt_decimal(value: float, places: int = 1) -> str:
    """Format decimal number, e.g., 2.48 -> '2.5'."""
    return f"{value:.{places}f}"


def fmt_price(value: float) -> str:
    """Format price, e.g., 2336 -> '£2,336'."""
    return f"£{value:,.0f}"


# =============================================================================
# Replacement functions by slide
# =============================================================================

def replace_slide2_market_overview(html: str, m: dict) -> str:
    """Slide 2: Market Overview - headline stats."""
    s = m["summary"]

    # Unique dogs for sale (first flow-number)
    html = re.sub(
        r'(<div class="flow-number">)[^<]+(</div>\s*<div class="flow-label">Unique dogs)',
        rf'\g<1>{fmt_k(s["unique_puppies"])}\2',
        html
    )

    # Annualized (second flow-number in flow)
    html = re.sub(
        r'(<div class="flow-number">)[^<]+(</div>\s*<div class="flow-label">Annualised)',
        rf'\g<1>{fmt_k(s["annualized_puppies"])}\2',
        html
    )

    # Market share percentage (third flow-number)
    html = re.sub(
        r'(<div class="flow-number">)[^<]+(</div>\s*<div class="flow-label">Of total UK market)',
        rf'\g<1>{fmt_pct(s["market_share_pct"])}\2',
        html
    )

    # Header: "X% of all dogs" - use rounded percentage
    headline_pct = round(s["market_share_pct"])
    html = re.sub(
        r'(<span>)[^<]+(</span> of all dogs sold)',
        rf'\g<1>{headline_pct}%\2',
        html
    )

    return html


def replace_slide3_journey(html: str, m: dict) -> str:
    """Slide 3: From Raw Listings to Unique Dogs."""
    s = m["summary"]

    # Raw listings (first hero-number)
    html = re.sub(
        r'(<div class="hero-number">)[^<]+(</div>\s*<div class="hero-label">Raw listings)',
        rf'\g<1>{fmt_k(s["raw_listings"])}\2',
        html
    )

    # Unique listings (second hero-number)
    html = re.sub(
        r'(<div class="hero-number">)[^<]+(</div>\s*<div class="hero-label">Unique listings)',
        rf'\g<1>{fmt_k(s["unique_listings"])}\2',
        html
    )

    # Unique dogs (third hero-number)
    html = re.sub(
        r'(<div class="hero-number">)[^<]+(</div>\s*<div class="hero-label">Unique dogs)',
        rf'\g<1>{fmt_k(s["unique_puppies"])}\2',
        html
    )

    # Header: "1 in X listings" and "Xk unique dogs"
    # Calculate cross-listing ratio
    cross_listed_pct = (s["raw_listings"] - s["unique_listings"]) / s["raw_listings"] * 100
    cross_listed_ratio = round(100 / cross_listed_pct) if cross_listed_pct > 0 else 5

    html = re.sub(
        r'(1 in )\d+( listings appear)',
        rf'\g<1>{cross_listed_ratio}\2',
        html
    )
    html = re.sub(
        r'(<span>)[^<]+k unique dogs(</span>)',
        rf'\g<1>{fmt_k(s["unique_puppies"])} unique dogs\2',
        html
    )

    # Duplicates removed card (within + cross only, not stale)
    within_dups = s.get("within_platform_dups", 0)
    cross_dups = s.get("cross_platform_dups", 0)
    total_dupes = within_dups + cross_dups
    dupes_display = fmt_comma(total_dupes) if total_dupes < 1000 else fmt_k(total_dupes)
    html = re.sub(
        r'(<div class="jc-icon">)-[\d,.]+k?(</div>\s*<div class="jc-title">Duplicates removed)',
        lambda m: f'{m.group(1)}-{dupes_display}{m.group(2)}',
        html
    )

    # Within-platform duplicates row
    html = re.sub(
        r'(<div class="jc-row"><span>Within-platform</span><span>)-[\d,]+(<\/span>)',
        lambda m: f'{m.group(1)}-{fmt_comma(within_dups)}{m.group(2)}',
        html
    )

    # Cross-platform duplicates row
    html = re.sub(
        r'(<div class="jc-row"><span>Cross-platform</span><span>)-[\d,]+(<\/span>)',
        lambda m: f'{m.group(1)}-{fmt_comma(cross_dups)}{m.group(2)}',
        html
    )

    # Stale removed card (separate box)
    stale_removed = s.get("stale_removed", 0)
    stale_display = fmt_comma(stale_removed) if stale_removed < 1000 else fmt_k(stale_removed)
    html = re.sub(
        r'(<div class="jc-icon">)-[\d,.]+k?(</div>\s*<div class="jc-title">Stale removed)',
        lambda m: f'{m.group(1)}-{stale_display}{m.group(2)}',
        html
    )

    # Dogs per listing
    avg_per = s["raw_avg_per_listing"]
    html = re.sub(
        r'(<div class="jc-icon">)×[\d.]+(<\/div>\s*<div class="jc-title">Dogs per listing)',
        rf'\g<1>×{fmt_decimal(avg_per)}\2',
        html
    )

    return html


def replace_slide4_platform_breakdown(html: str, m: dict) -> str:
    """Slide 4: Platform Breakdown table."""
    platforms = m["platforms"]

    # Platform order as in HTML
    platform_order = [
        ("pets4homes", "Pets4Homes"),
        ("freeads", "FreeAds"),
        ("gumtree", "Gumtree"),
        ("petify", "Petify"),
        ("foreverpuppy", "ForeverPuppy"),
        ("kennel_club", "Kennel Club"),
        ("puppies", "Puppies.co.uk"),
        ("preloved", "Preloved"),
        ("champdogs", "Champdogs"),
    ]

    for key, name in platform_order:
        if key not in platforms:
            continue
        p = platforms[key]
        listings_str = fmt_comma(p["listings"])
        puppies_str = fmt_comma(p["puppies"])
        avg_str = fmt_decimal(p["avg"])

        # Match the table row for this platform and update values
        # Pattern: platform name ... listings ... puppies ... avg
        pattern = rf'(<span class="platform-dot[^"]*"></span>{re.escape(name)}\s*</div>\s*<div class="td td-num">)[^<]+(</div>\s*<div class="td td-num">)[^<]+(</div>\s*<div class="td td-highlight">)[^<]+(</div>)'

        def make_replacement(l, p, a):
            return lambda match: f'{match.group(1)}{l}{match.group(2)}{p}{match.group(3)}{a}{match.group(4)}'

        html = re.sub(pattern, make_replacement(listings_str, puppies_str, avg_str), html)

    # Total row
    total_listings = sum(p["listings"] for p in platforms.values())
    total_puppies = sum(p["puppies"] for p in platforms.values())
    total_avg = total_puppies / total_listings if total_listings > 0 else 0

    total_l = fmt_comma(total_listings)
    total_p = fmt_comma(total_puppies)
    total_a = fmt_decimal(total_avg)

    html = re.sub(
        r'(<div class="tf tf-platform">Total</div>\s*<div class="tf tf-num">)[^<]+(</div>\s*<div class="tf tf-num">)[^<]+(</div>\s*<div class="tf tf-highlight">)[^<]+(</div>)',
        lambda match: f'{match.group(1)}{total_l}{match.group(2)}{total_p}{match.group(3)}{total_a}{match.group(4)}',
        html
    )

    # Insight panel - Pets4Homes share
    p4h_share = platforms["pets4homes"]["puppies"] / total_puppies * 100 if total_puppies > 0 else 0
    html = re.sub(
        r'(<div class="insight-value">)[^<]+(</div>\s*<div class="insight-label">Pets4Homes share)',
        rf'\g<1>{fmt_pct(p4h_share)}\2',
        html
    )

    return html


def replace_slide5_duplication(html: str, m: dict) -> str:
    """Slide 5: Cross-Platform Duplication."""
    platforms = m["platforms"]

    # Calculate unique percentages (this is derived - unique / total)
    # The HTML shows "% Unique" which we need to calculate from the data
    # For now, use the 'unique' field from platforms

    platform_unique_map = [
        ("ForeverPuppy", "foreverpuppy"),
        ("Kennel Club", "kennel_club"),
        ("Champdogs", "champdogs"),
        ("Preloved", "preloved"),
        ("Pets4Homes", "pets4homes"),
        ("Puppies.co.uk", "puppies"),
        ("FreeAds", "freeads"),
        ("Gumtree", "gumtree"),
        ("Petify", "petify"),
    ]

    for display_name, key in platform_unique_map:
        if key not in platforms:
            continue
        p = platforms[key]
        total = p["listings"]
        unique = p["unique"]
        pct = round(unique / total * 100) if total > 0 else 0

        total_str = fmt_comma(total)
        unique_str = fmt_comma(unique)
        pct_str = f"{pct}%"

        # Match: platform name ... total ... unique ... pct
        pattern = rf'(<span class="seller-name">{re.escape(display_name)}</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-pct">)[^<]+(</span>)'

        def make_repl(t, u, p):
            return lambda match: f'{match.group(1)}{t}{match.group(2)}{u}{match.group(3)}{p}{match.group(4)}'

        html = re.sub(pattern, make_repl(total_str, unique_str, pct_str), html, count=1)

    # Cross-platform duplicates removed (single value from summary)
    s = m["summary"]
    cross_dups = s.get("cross_platform_dups", 0)

    html = re.sub(
        r'(<span class="mini-label">Duplicates removed</span>\s*<span class="mini-val">)[^<]+(</span>)',
        rf'\g<1>{fmt_comma(cross_dups)}\2',
        html
    )

    # Platform pair overlap - inject from canonical metrics
    pair_overlap = m.get("platform_pair_overlap", [])

    # Mapping from JSON platform names to display names
    display_names = {
        'gumtree': 'Gumtree',
        'pets4homes': 'P4H',
        'freeads': 'FreeAds',
        'puppies': 'Puppies',
        'petify': 'Petify',
        'preloved': 'Preloved',
        'kennel_club': 'KC',
        'foreverpuppy': 'ForeverPuppy',
        'champdogs': 'Champdogs',
    }

    # Update each platform pair row
    for pair_data in pair_overlap[:6]:  # Top 6 pairs shown in slide
        p1, p2 = pair_data['platforms']
        d1, d2 = display_names.get(p1, p1), display_names.get(p2, p2)
        count = pair_data['count']
        pct = pair_data['pct']

        # Match pattern: "Platform1 ↔ Platform2" with count and pct
        # The arrow character is ↔ (unicode)
        pattern = rf'(<span class="mini-label">{re.escape(d1)} ↔ {re.escape(d2)}</span>\s*<span class="mini-count">)[^<]+(</span>\s*<span class="mini-pct">)[^<]+(</span>)'

        def make_pair_repl(c, p):
            return lambda m: f'{m.group(1)}{c}{m.group(2)}{p}%{m.group(3)}'

        html = re.sub(pattern, make_pair_repl(count, pct), html)

    # Header update with lowest uniqueness platform
    lowest_unique_pct = 100
    lowest_platform = "Petify"
    for key, p in platforms.items():
        if p["listings"] > 0:
            pct = p["unique"] / p["listings"] * 100
            if pct < lowest_unique_pct:
                lowest_unique_pct = pct
                lowest_platform = key.replace("_", " ").title()
                if key == "pets4homes":
                    lowest_platform = "Pets4Homes"
                elif key == "foreverpuppy":
                    lowest_platform = "ForeverPuppy"

    html = re.sub(
        r'(Only <span>)[^<]+(</span> of )\w+( inventory is unique)',
        rf'\g<1>{fmt_pct(lowest_unique_pct)}\2{lowest_platform}\3',
        html
    )

    return html


def replace_slide6_sellers(html: str, m: dict) -> str:
    """Slide 6: Seller Analysis."""
    sellers = m["sellers"]
    by_platform = sellers.get("by_platform", {})

    # Header: X% of sellers have just one listing
    pct_one = sellers.get("pct_one_listing", 94)
    html = re.sub(
        r'(<h1><span>)\d+(%</span> of sellers have just one listing)',
        rf'\g<1>{pct_one}\2',
        html
    )

    # Seller Distribution by Platform table
    platform_display = [
        ("Pets4Homes", "pets4homes"),
        ("FreeAds", "freeads"),
        ("Gumtree", "gumtree"),
        ("ForeverPuppy", "foreverpuppy"),
        ("Puppies.co.uk", "puppies"),
        ("Preloved", "preloved"),
    ]

    for display_name, key in platform_display:
        if key not in by_platform:
            continue
        p = by_platform[key]
        sellers_str = fmt_comma(p["total_sellers"])
        pct_str = f"{p['pct_one_listing']}%"
        max_str = str(p["max_listings"])

        # Match: platform name ... sellers ... % 1 list ... max
        pattern = rf'(<span class="seller-name">{re.escape(display_name)}</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-pct">)[^<]+(</span>\s*<span class="seller-listings">)[^<]+(</span>)'

        def make_seller_repl(s, pct, mx):
            return lambda match: f'{match.group(1)}{s}{match.group(2)}{pct}{match.group(3)}{mx}{match.group(4)}'

        html = re.sub(pattern, make_seller_repl(sellers_str, pct_str, max_str), html)

    # Summary section
    html = re.sub(
        r'(<span class="mini-label">Total unique sellers</span>\s*<span class="mini-val">)[^<]+(</span>)',
        rf'\g<1>{fmt_comma(sellers["total"])}\2',
        html
    )
    html = re.sub(
        r'(<span class="mini-label">With 1 listing only</span>\s*<span class="mini-val">)[^<]+(</span>)',
        rf'\g<1>{pct_one}%\2',
        html
    )
    html = re.sub(
        r'(<span class="mini-label">Confirmed rescues</span>\s*<span class="mini-val">)[^<]+(</span>)',
        rf'\g<1>{sellers.get("rescue_count", 0)}\2',
        html
    )

    # Top sellers table - rebuild entire table from canonical data
    top_10 = sellers.get("top_10", [])

    # Platform name mapping for display
    plat_display = {
        'pets4homes': 'P4H',
        'freeads': 'FreeAds',
        'gumtree': 'Gumtree',
        'foreverpuppy': 'ForeverPuppy',
        'puppies': 'Puppies',
        'preloved': 'Preloved',
        'kennel_club': 'KC',
        'champdogs': 'Champdogs',
        'petify': 'Petify',
    }

    # Build new table rows
    rows_html = []
    for i, seller in enumerate(top_10, 1):
        is_rescue = seller.get("is_rescue", False)
        if is_rescue:
            bg_color = "rgba(20, 184, 166, 0.1)"
            text_color = "#14b8a6"
        else:
            bg_color = "rgba(251, 191, 36, 0.1)"
            text_color = "#fbbf24"

        name = seller["name"]
        listings = seller["listings"]
        platforms = [plat_display.get(p, p) for p in seller.get("platforms", [])]
        plat_str = ", ".join(platforms)

        row = f'''                <div class="seller-row" style="background: {bg_color};">
                    <span class="seller-rank" style="color: {text_color};">{i}</span>
                    <span class="seller-name" style="color: {text_color};">{name}</span>
                    <span class="seller-listings">{listings}</span>
                    <span class="seller-platforms">{plat_str}</span>
                </div>'''
        rows_html.append(row)

    new_table = "\n".join(rows_html)

    # Replace the entire top sellers table body (between header and legend)
    pattern = r'(<div class="table-section-label">Top Sellers</div>\s*<div class="seller-table">\s*<div class="seller-row seller-header">.*?</div>)\s*(?:<div class="seller-row".*?</div>\s*)+(<div style="font-size: 9px)'

    def table_replacer(match):
        return f'{match.group(1)}\n{new_table}\n            </div>\n            {match.group(2)}'

    html = re.sub(pattern, table_replacer, html, flags=re.DOTALL)

    return html


def replace_slide7_welfare(html: str, m: dict) -> str:
    """Slide 7: Welfare & Regulation - high volume sellers."""
    sellers = m["sellers"]
    by_platform = sellers.get("by_platform", {})
    total_hv = sellers.get("high_volume", 1)

    # Header: X% of high-volume sellers are on FreeAds
    freeads_hv = by_platform.get("freeads", {}).get("high_volume", 0)
    freeads_pct = round(freeads_hv / total_hv * 100) if total_hv > 0 else 0

    html = re.sub(
        r'(<span>)[^<]+(</span> of high-volume sellers are on FreeAds)',
        rf'\g<1>{freeads_pct}%\2',
        html
    )

    # License Tracking table - update each platform row (top 3 by HV count)
    license_platforms = [
        ("FreeAds", "freeads", "None", "#ef4444"),
        ("Pets4Homes", "pets4homes", "Yes", "#34d399"),
        ("Preloved", "preloved", "None", "#ef4444"),
    ]

    for display_name, key, tracking, color in license_platforms:
        if key not in by_platform:
            continue
        p = by_platform[key]
        hv_count = p.get("high_volume", 0)
        lic_pct = p.get("license_pct", 0)

        # Format license percentage
        if tracking == "Enforced":
            pct_str = "✓"
        elif lic_pct > 0:
            pct_str = f"{round(lic_pct)}%"
        else:
            pct_str = "0%"

        # Match and update the row
        pattern = rf'(<span class="seller-name">{re.escape(display_name)}</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-platforms"[^>]*>)[^<]+(</span>\s*<span class="seller-pct"[^>]*>)[^<]+(</span>)'

        def make_lic_repl(cnt, trk, pct):
            return lambda match: f'{match.group(1)}{cnt}{match.group(2)}{trk}{match.group(3)}{pct}{match.group(4)}'

        html = re.sub(pattern, make_lic_repl(hv_count, tracking, pct_str), html)

    # Top Breeders table - rebuild from top_10 (excluding rescues, 3+ listings)
    top_10 = sellers.get("top_10", [])
    breeders = [s for s in top_10 if not s.get("is_rescue", False) and s.get("listings", 0) >= 3][:5]

    plat_display = {
        'pets4homes': 'P4H',
        'freeads': 'FreeAds',
        'gumtree': 'Gumtree',
        'preloved': 'Preloved',
        'foreverpuppy': 'ForeverPuppy',
        'puppies': 'Puppies',
        'kennel_club': 'KC',
    }

    # Build new breeder rows
    breeder_rows = []
    for seller in breeders:
        has_license = seller.get("has_license", False)
        if has_license:
            bg_style = 'style="background: rgba(52, 211, 153, 0.08);"'
            lic_style = 'style="color: #34d399;"'
            lic_icon = "✓"
        else:
            bg_style = ''
            lic_style = 'style="color: #5a4a3a;"'
            lic_icon = "—"

        name = seller["name"][:18]  # Truncate long names
        listings = seller["listings"]
        platforms = [plat_display.get(p, p) for p in seller.get("platforms", [])]
        plat_str = ", ".join(platforms)

        row = f'''                <div class="seller-row" {bg_style}>
                    <span class="seller-name">{name}</span>
                    <span class="seller-listings">{listings}</span>
                    <span class="seller-platforms">{plat_str}</span>
                    <span class="seller-pct" {lic_style}>{lic_icon}</span>
                </div>'''
        breeder_rows.append(row)

    new_breeders = "\n".join(breeder_rows)

    # Replace the Top Breeders table body
    pattern = r'(<div class="table-section-label spaced">Top Breeders \(3\+ listings\)</div>\s*<div class="seller-table">\s*<div class="seller-row seller-header">.*?</div>)\s*(?:<div class="seller-row".*?</div>\s*)+(</div>\s*</div>)'

    def breeders_replacer(match):
        return f'{match.group(1)}\n{new_breeders}\n            {match.group(2)}'

    html = re.sub(pattern, breeders_replacer, html, flags=re.DOTALL)

    return html


def replace_slide8_freshness(html: str, m: dict) -> str:
    """Slide 8: Listing Freshness."""
    freshness = m["freshness"]

    # Median days bars
    platform_freshness = [
        ("Gumtree", "gumtree"),
        ("Pets4Homes", "pets4homes"),
        ("FreeAds", "freeads"),
        ("ForeverPuppy", "foreverpuppy"),
        ("Preloved", "preloved"),
        ("Puppies.co.uk", "puppies"),
        ("Petify", "petify"),
    ]

    for display_name, key in platform_freshness:
        if key not in freshness:
            continue
        f = freshness[key]
        median = f.get("median_days")
        if median is None:
            continue

        # Update bar value text
        pattern = rf'(<span class="freshness-label">{re.escape(display_name)}</span>.*?<span class="bar-value">)[^<]+(</span>)'
        replacement = rf'\g<1>{median} days\2'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    # Age distribution table percentages
    for display_name, key in platform_freshness:
        if key not in freshness:
            continue
        f = freshness[key]

        u7 = f"{f.get('under_7d_pct', 0)}%"
        d7_30 = f"{f.get('7_30d_pct', 0)}%"
        d30_90 = f"{f.get('30_90d_pct', 0)}%"
        o90 = f"{f.get('over_90d_pct', 0)}%"

        # Match the age-row for this platform
        pattern = rf'(<span class="age-platform">{re.escape(display_name)}</span>\s*<span class="age-val[^"]*">)[^<]+(</span>\s*<span class="age-val[^"]*">)[^<]+(</span>\s*<span class="age-val[^"]*">)[^<]+(</span>\s*<span class="age-val[^"]*">)[^<]+(</span>)'

        def make_age_repl(a, b, c, d):
            return lambda m: f'{m.group(1)}{a}{m.group(2)}{b}{m.group(3)}{c}{m.group(4)}{d}{m.group(5)}'

        html = re.sub(pattern, make_age_repl(u7, d7_30, d30_90, o90), html)

    # Header - find platform with most stale listings
    max_stale = 0
    stalest_platform = "Petify"
    for key, f in freshness.items():
        stale = f.get("over_90d_pct", 0)
        if stale > max_stale:
            max_stale = stale
            stalest_platform = key.replace("_", " ").title()
            if key == "pets4homes":
                stalest_platform = "Pets4Homes"
            elif key == "foreverpuppy":
                stalest_platform = "ForeverPuppy"

    # Find freshest platform
    min_median = 999
    freshest_platform = "Gumtree"
    for key, f in freshness.items():
        median = f.get("median_days")
        if median is not None and median < min_median:
            min_median = median
            freshest_platform = key.replace("_", " ").title()
            if key == "pets4homes":
                freshest_platform = "Pets4Homes"
            elif key == "foreverpuppy":
                freshest_platform = "ForeverPuppy"

    html = re.sub(
        r'(<span>)[^<]+(</span> of \w+ listings are over)',
        rf'\g<1>{max_stale}%\2',
        html
    )
    html = re.sub(
        r'(listings are over [^—]+— \s*)\w+( is the freshest)',
        rf'\g<1>{freshest_platform}\2',
        html
    )

    return html


def replace_slide9_puppy_age(html: str, m: dict) -> str:
    """Slide 9: Puppy Age Profile."""
    age_dist = m["age_distribution"]
    pva = m["puppies_vs_adults"]

    # Platform order as shown in slide
    platform_order = [
        ("Gumtree", "gumtree"),
        ("Pets4Homes", "pets4homes"),
        ("Kennel Club", "kennel_club"),
        ("FreeAds", "freeads"),
        ("ForeverPuppy", "foreverpuppy"),
        ("Champdogs", "champdogs"),
        ("Preloved", "preloved"),
    ]

    for display_name, key in platform_order:
        if key not in age_dist:
            continue
        a = age_dist[key]
        u8 = a.get('under_8w', 0)
        w8_12 = a.get('8-12w', 0)
        w12_26 = a.get('12-26w', 0)
        m6_12 = a.get('6-12mo', 0)
        o1yr = a.get('over_1yr', 0)
        median = a.get('median_weeks', 0)

        # Update each segment width in the stacked bar
        # Pattern: find the stacked-row for this platform and update segment widths
        # Match the row by platform label and update all segments

        # Update <8 weeks segment
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>\s*<div class="stacked-bar-container">\s*<div class="stack-segment stack-too-young" style="width: )\d+(%;" title="<8 weeks: )\d+(%"></div>)'
        html = re.sub(pattern, rf'\g<1>{u8}\g<2>{u8}\3', html)

        # Update 8-12 weeks segment
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>.*?stack-too-young.*?<div class="stack-segment stack-ideal" style="width: )\d+(%;" title="8-12 weeks: )\d+(%"></div>)'
        html = re.sub(pattern, rf'\g<1>{w8_12}\g<2>{w8_12}\3', html, flags=re.DOTALL)

        # Update 12-26 weeks segment
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>.*?stack-ideal.*?<div class="stack-segment stack-young" style="width: )\d+(%;" title="12-26 weeks: )\d+(%"></div>)'
        html = re.sub(pattern, rf'\g<1>{w12_26}\g<2>{w12_26}\3', html, flags=re.DOTALL)

        # Update 6mo-1yr segment
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>.*?stack-young.*?<div class="stack-segment stack-adolescent" style="width: )\d+(%;" title="6mo-1yr: )\d+(%"></div>)'
        html = re.sub(pattern, rf'\g<1>{m6_12}\g<2>{m6_12}\3', html, flags=re.DOTALL)

        # Update >1yr segment
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>.*?stack-adolescent.*?<div class="stack-segment stack-adult" style="width: )\d+(%;" title=">1yr: )\d+(%"></div>)'
        html = re.sub(pattern, rf'\g<1>{o1yr}\g<2>{o1yr}\3', html, flags=re.DOTALL)

        # Update median weeks
        pattern = rf'(<span class="stacked-label">{re.escape(display_name)}</span>.*?<span class="stacked-median">)\d+wk(</span>)'
        html = re.sub(pattern, rf'\g<1>{median}wk\2', html, flags=re.DOTALL)

    # Update Preloved insight card (40% adult dogs)
    preloved_adult = age_dist.get("preloved", {}).get("over_1yr", 40)
    html = re.sub(
        r'(<div class="age-insight-stat"[^>]*>)\d+%(</div>\s*<div class="age-insight-text">Preloved listings are adult dogs)',
        rf'\g<1>{preloved_adult}%\2',
        html
    )

    return html


def replace_slide10_regulation(html: str, m: dict) -> str:
    """Slide 10: 8-Week Regulation compliance."""
    reg = m.get("eight_week_regulation", {})

    # Update each platform row in the Ready-to-Leave Enforcement table
    # This table is unique to slide 10 and follows the "Ready-to-Leave Enforcement" heading

    def make_replacer(count, protected_label, pct):
        def replacer(match):
            return f'{match.group(1)}{count}{match.group(2)}{protected_label}{match.group(3)}{pct}%{match.group(4)}'
        return replacer

    # Pets4Homes: update count, change "Yes" to "Enforced", update percentage
    if "pets4homes" in reg:
        r = reg["pets4homes"]
        pattern = r'(Ready-to-Leave Enforcement</div>.*?<span class="seller-name">Pets4Homes</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-platforms"[^>]*>)[^<]+(</span>\s*<span class="seller-pct">)[^<]+(</span>)'
        html = re.sub(pattern, make_replacer(fmt_comma(r["total_under_8w"]), "Enforced", r["pct_protected"]), html, flags=re.DOTALL)

    # Gumtree: update count, set "Enforced", update percentage
    if "gumtree" in reg:
        r = reg["gumtree"]
        pattern = r'(Ready-to-Leave Enforcement</div>.*?<span class="seller-name">Gumtree</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-platforms"[^>]*>)[^<]+(</span>\s*<span class="seller-pct">)[^<]+(</span>)'
        html = re.sub(pattern, make_replacer(fmt_comma(r["total_under_8w"]), "Enforced", r["pct_protected"]), html, flags=re.DOTALL)

    # FreeAds: update count, change "None" to "Optional", update percentage
    if "freeads" in reg:
        r = reg["freeads"]
        pattern = r'(Ready-to-Leave Enforcement</div>.*?<span class="seller-name">FreeAds</span>\s*<span class="seller-listings">)[^<]+(</span>\s*<span class="seller-platforms"[^>]*>)[^<]+(</span>\s*<span class="seller-pct">)[^<]+(</span>)'
        html = re.sub(pattern, make_replacer(fmt_comma(r["total_under_8w"]), "Optional", r["pct_protected"]), html, flags=re.DOTALL)

    # Update the FreeAds insight text
    freeads_data = reg.get("freeads", {})
    total_freeads = freeads_data.get("total_under_8w", 559)
    no_ready = freeads_data.get("no_ready_date", 432)
    pct_no_ready = round(100 * no_ready / total_freeads) if total_freeads > 0 else 77

    # Update "559 puppies under 8 weeks — 77% have no ready date"
    html = re.sub(
        r'(\d+) puppies under 8 weeks — (\d+)% have no ready date',
        f'{total_freeads} puppies under 8 weeks — {pct_no_ready}% have no ready date',
        html
    )

    # Update "432 puppies" stat
    html = re.sub(
        r'(\d+) puppies(</div>\s*<div class="age-insight-text">under 8 weeks on FreeAds)',
        rf'{no_ready} puppies\2',
        html
    )

    return html


def replace_slide11_breeds(html: str, m: dict) -> str:
    """Slide 11: Top Breeds."""
    breeds = m["breeds"]
    top_count = breeds.get("top_by_count", [])
    top_price = breeds.get("top_by_price", [])

    # Update header with top breed info
    if top_count:
        top_breed = top_count[0]
        breed_name = top_breed["breed"]
        breed_count = fmt_comma(top_breed["count"])
        html = re.sub(
            r'(<span>)[^<]+(</span> is most popular with )[^—]+(—)',
            lambda match: f'{match.group(1)}{breed_name}{match.group(2)}{breed_count} dogs for sale {match.group(3)}',
            html
        )

    if top_price:
        # Find highest price breed
        top_price_breed = top_price[0]
        price_breed = top_price_breed["breed"]
        price_val = fmt_price(top_price_breed["avg_price"])
        # Match multi-word breed name before "commands highest prices"
        html = re.sub(
            r'[A-Z][\w\s]+(?= commands highest prices at £)',
            price_breed,
            html
        )
        # Update the price value
        html = re.sub(
            r'(commands highest prices at )£[\d,]+',
            rf'\1{price_val}',
            html
        )

    # Rebuild the Top 10 by Count table with ranking
    if top_count:
        rows_html = '''                <div class="seller-row seller-header">
                    <span class="seller-rank">#</span>
                    <span class="seller-name">Breed</span>
                    <span class="seller-listings">Dogs</span>
                    <span class="seller-pct">%</span>
                </div>\n'''
        for i, b in enumerate(top_count[:10]):
            highlight = ' style="background: rgba(251, 191, 36, 0.1);"' if i == 0 else ''
            pct_style = ' style="color: #fbbf24;"' if i == 0 else ''
            rows_html += f'''                <div class="seller-row"{highlight}>
                    <span class="seller-rank">{i+1}</span>
                    <span class="seller-name">{b["breed"]}</span>
                    <span class="seller-listings">{fmt_comma(b["count"])}</span>
                    <span class="seller-pct"{pct_style}>{b["share"]}%</span>
                </div>\n'''

        # Replace the entire seller-table for breeds
        pattern = r'(Top 10 Breeds by Dogs for Sale</div>\s*<div class="seller-table">).*?(</div>\s*</div>\s*\n\s*<div class="dual-table-right">)'
        html = re.sub(pattern, rf'\1\n{rows_html}            \2', html, flags=re.DOTALL)

    # Rebuild the Most Expensive Breeds table (no bars, with ranking)
    if top_price:
        rows_html = '''                <div class="seller-row seller-header">
                    <span class="seller-rank">#</span>
                    <span class="seller-name">Breed</span>
                    <span class="seller-listings">Dogs</span>
                    <span class="seller-pct">Price</span>
                </div>\n'''
        for i, b in enumerate(top_price[:10]):
            highlight = ' style="background: rgba(251, 191, 36, 0.1);"' if i == 0 else ''
            puppies = b.get("puppies", b.get("count", 0))
            rows_html += f'''                <div class="seller-row"{highlight}>
                    <span class="seller-rank">{i+1}</span>
                    <span class="seller-name">{b["breed"]}</span>
                    <span class="seller-listings">{fmt_comma(puppies)}</span>
                    <span class="seller-pct">{fmt_price(b["avg_price"])}</span>
                </div>\n'''

        # Replace the price-bars section with a seller-table
        pattern = r'(Most Expensive Breeds \(avg price\)</div>\s*)<div class="price-bars">.*?(</div>\s*</div>\s*</div>\s*<div class="slide-number">11)'
        replacement = rf'\1<div class="seller-table">\n{rows_html}            </div>\n        </div>\n    </div>\n    \2'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    return html


# =============================================================================
# Main orchestration
# =============================================================================

def generate_slides():
    """Main function to generate updated slides."""
    print("Loading metrics from", METRICS_PATH)
    metrics = load_metrics(METRICS_PATH)

    print("Loading HTML template from", HTML_PATH)
    html = load_html(HTML_PATH)

    print("Applying replacements...")

    # Apply replacements slide by slide
    html = replace_slide2_market_overview(html, metrics)
    html = replace_slide3_journey(html, metrics)
    html = replace_slide4_platform_breakdown(html, metrics)
    # Slide 5 (was 6): Seller Analysis
    html = replace_slide6_sellers(html, metrics)
    # Slide 6 (was 7): Welfare & Regulation
    html = replace_slide7_welfare(html, metrics)
    # Slide 7 (was 8): Listing Freshness
    html = replace_slide8_freshness(html, metrics)
    # Slide 8 (was 9): Puppy Age Profile
    html = replace_slide9_puppy_age(html, metrics)
    # Slide 9 (was 10): 8-Week Regulation
    html = replace_slide10_regulation(html, metrics)
    # Slide 10 (was 11): Top Breeds
    html = replace_slide11_breeds(html, metrics)
    # Slide 11: Geography (new, static data in HTML)

    print("Saving updated HTML to", HTML_PATH)
    save_html(HTML_PATH, html)

    print("Done!")


if __name__ == "__main__":
    generate_slides()
