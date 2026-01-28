# UK Puppy Market Welfare Intelligence Report

A Reveal.js presentation for animal welfare charities (Battersea, PAAG, Naturewatch), providing evidence-based insights into the UK online puppy market.

## Quick Start

```bash
# Build the presentation
python3 charity_deck/build_deck.py

# Serve locally (open http://localhost:8000)
cd charity_deck
python3 -m http.server 8000

# Export to PDF
python3 scripts/export_pdf.py
```

## Focus Areas

This deck reframes the market data for welfare advocacy:

| Topic | Key Finding |
|-------|-------------|
| **License Compliance** | ~71% of high-volume sellers have no displayed license |
| **Lucy's Law** | FreeAds has 559 under-8-week puppies with only 4% protected |
| **Platform Accountability** | 47% of high-volume sellers on platforms with no verification |
| **Geographic Hotspots** | Wisbech (pop. 35k) ranks #8 nationwide for dogs listed |
| **At-Risk Breeds** | French Bulldogs most popular + brachycephalic welfare concerns |

## Slides Overview

1. **Cover** - UK Puppy Market Welfare Intelligence Report
2. **Why This Matters** - Puppy farming, regulation gaps, data enables action
3. **Market Scale** - 59k dogs, 19k listings, 10 platforms
4. **Platform Breakdown** - Pets4Homes dominates at 50%
5. **License Compliance Gap** - Only 29% of high-volume sellers licensed
6. **Lucy's Law Compliance** - 8-week rule enforcement varies by platform
7. **Red Flags** - Unlicensed high-volume sellers list
8. **Geographic Hotspots** - Areas for enforcement priority
9. **Pricing Patterns** - Premium breeds and welfare signals
10. **Summary** - Key findings for welfare advocacy
11. **Recommendations** - Actions for platforms, LAs, charities
12. **Methodology** - Data sources and limitations
13. **Close**

## Data Source

All data comes from `canonical_metrics.json` in the project root (same source as gumtree_deck). The build script computes additional welfare-focused metrics:

- `welfare.total_high_volume` - Total sellers with 3+ listings
- `welfare.total_licensed` - Those with displayed license
- `welfare.license_rate_pct` - Overall license display rate
- `welfare.unlicensed_breeders` - Top unlicensed high-volume sellers

## Customization

### Changing the colour scheme

The deck uses a green/red welfare colour scheme instead of orange. Edit the CSS variables in `templates/index.html.j2`:

```css
:root {
    --welfare-red: #ef4444;
    --welfare-amber: #f59e0b;
    --welfare-green: #10b981;
    --welfare-blue: #3b82f6;
}
```

### Adding branding

To add charity branding, edit the cover slide and `deck-title` / `slide-logo` elements in the template.

## Rebuilding

```bash
# After any changes to canonical_metrics.json
python3 charity_deck/build_deck.py
python3 charity_deck/scripts/export_pdf.py
```
