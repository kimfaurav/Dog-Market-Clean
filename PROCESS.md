# Dog Market Intelligence - End-to-End Process

This document captures the complete process for regenerating the dog market analysis and presentation deck, including all platform-specific quirks and data quality fixes learned through iteration.

## Quick Reference: Full Rebuild

```bash
# 1. Run scrapers (if data refresh needed)
cd scrapers
python3 pets4homes_scraper.py
python3 gumtree_scraper.py
# ... etc for each platform

# 2. Run pipeline to build derived.csv
cd ..
python3 pipeline/run_pipeline.py

# 3. Generate canonical metrics
python3 canonical_metrics.py

# 4. Build presentation deck
python3 gumtree_deck/build_deck.py

# 5. Export PDF
python3 gumtree_deck/scripts/export_pdf.py
```

## Data Flow

```
scrapers/                    Input/Raw CSVs/           output/views/
├── pets4homes_scraper.py    ├── pets4homes_data.csv   ├── derived.csv
├── gumtree_scraper.py   →   ├── gumtree_data.csv  →   └── (other views)
├── preloved_scraper.py      ├── preloved_data.csv            ↓
├── freeads_scraper.py       ├── freeads_data.csv     canonical_metrics.json
├── petify_scraper.py        ├── petify_data_v3.csv           ↓
├── ...                      └── ...                  gumtree_deck/
                                                      ├── templates/index.html.j2
                                                      ├── index.html (generated)
                                                      └── deck.pdf (generated)
```

## Platform-Specific Data Quality Notes

### Pets4Homes
- **License tracking**: Has `license_num` field - most complete license data
- **Seller identification**: `seller_name` + `location` for seller_key
- **Coverage**: ~7,600 listings, highest volume platform
- **License compliance**: ~81.5% of high-volume sellers have licenses

### Preloved
- **License tracking**: Via `user_type` field, NOT `license_num`
  - `user_type='Licensed Breeder'` indicates licensed
  - Must map this to license_num in canonical_metrics.py:
    ```python
    licensed_breeder_mask = df['user_type'] == 'Licensed Breeder'
    df.loc[licensed_breeder_mask & df['license_num'].isna(), 'license_num'] = 'LICENSED'
    ```
- **License compliance**: ~15.4% of high-volume sellers have licenses
- **Coverage**: ~700 listings

### Petify
- **CRITICAL**: Only provides seller INITIALS, not full names
- **Scraper bug history**: Original scraper extracted "Since J" (from "Member since January") as seller name
- **Current handling**: Exclude from seller analysis entirely:
  ```python
  df.loc[df['platform'] == 'petify', 'seller_key'] = 'UNKNOWN|UNKNOWN'
  ```
- **Usable for**: Price, breed, location, health checks - NOT seller identification
- **Coverage**: ~430 listings

### Gumtree
- **Good data quality**: Has seller_name, location
- **Coverage**: ~1,800 listings

### Freeads
- **Large volume but lower data quality**
- **Date parsing**: Uses anchoring heuristics (see pipeline README)
- **Coverage**: ~6,500 listings

### Kennel Club
- **Official KC registered breeders only**
- **Litter size**: Parse "X Bitch, Y Dog" format
- **Coverage**: ~400 listings

### Gundogs Direct
- **Niche platform for working dogs**
- **Coverage**: ~100 listings

### Champdogs
- **Show dog focused**
- **puppies_available field is NULL** (scraper limitation)
- **Coverage**: ~160 listings

### ForeverPuppy
- **Aggregator site**
- **Coverage**: ~600 listings

### Puppies.co.uk
- **Coverage**: ~575 listings

## Seller Analysis Rules

### Exclusions from Seller Statistics

1. **Stud services**: Filter out listings with stud-related titles
   ```python
   stud_pattern = r'\b(stud|at stud|stud service|stud dog|stud only)\b'
   df = df[~df['title'].str.contains(stud_pattern, case=False, na=False)]
   ```

2. **Rescues**: Exclude from license requirement calculations
   - Rescues don't need breeding licenses
   - Identify via seller_name patterns or dedicated rescue platforms

3. **Petify**: Exclude entirely (only has initials)

### Seller Key Construction

```python
# Standard pattern: name|location (lowercase, stripped)
seller_key = f"{seller_name.lower().strip()}|{location.lower().strip()}"
```

### High-Volume Seller Definition
- 3+ listings = high-volume seller (requires breeding license)

## License Compliance Calculation

```python
# Exclude rescues from denominator
non_rescue_high_volume = high_volume_sellers[~is_rescue]
licensed_count = non_rescue_high_volume[has_license].count()
license_pct = licensed_count / len(non_rescue_high_volume) * 100
```

## Canonical Metrics Generation

The `canonical_metrics.py` script generates `canonical_metrics.json` which contains:

- **summary**: Total listings, unique puppies, market share estimates
- **platforms**: Per-platform breakdown (listings, puppies, share, freshness)
- **sellers**:
  - total count, single-listing %, top 10 sellers
  - by_platform: high_volume count, license_pct per platform
- **breeds**: Top breeds by count and price
- **geography**: Top cities, regions, hotspots
- **freshness**: Per-platform data freshness metrics
- **age_distribution**: Puppy age breakdowns
- **eight_week_regulation**: Lucy's Law compliance metrics

## Presentation Deck Build

### Template System

The deck uses Jinja2 templating:

```
gumtree_deck/
├── templates/
│   └── index.html.j2    # Template with {{ variable }} bindings
├── build_deck.py        # Renders template with canonical_metrics.json
├── index.html           # Generated output (git-tracked)
└── deck.pdf             # Generated PDF
```

### Custom Jinja2 Filters

Defined in `build_deck.py`:

| Filter | Purpose | Example |
|--------|---------|---------|
| `format_k` | Thousands with k suffix | 59000 → "59k" |
| `format_comma` | Comma-separated | 59000 → "59,000" |
| `format_pct` | Percentage | 0.815 → "81.5%" |
| `format_int` | Integer | 81.5 → "82" |
| `format_price` | Currency | 1500 → "£1,500" |

### Slide Data Bindings

| Slide | Data Source |
|-------|-------------|
| 6 - Market Coverage | `summary.unique_puppies`, `summary.annualized_puppies` |
| 7 - Deduplication | `summary.raw_listings`, `summary.unique_listings` |
| 8 - Platform Table | `platforms.*` (loop) |
| 9 - Top Sellers | `sellers.top_10` (loop) |
| 10 - Compliance | `sellers.by_platform.*.license_pct` |
| 14 - Top Breeds | `breeds.top_by_count`, `breeds.top_by_price` |
| 15 - Geography | `geography.top_cities`, `geography.top_regions` |

## Validation Checklist

Before committing regenerated data:

1. **Check for garbage seller names**
   - Look for patterns like "Since J", "Since M" (Petify bug)
   - Verify top 10 sellers are real names, not parsing artifacts

2. **Verify license percentages**
   - P4H should be ~80%+ (has good license tracking)
   - Preloved should be ~15% (via user_type mapping)
   - Platforms without tracking should show "None"

3. **Confirm exclusions applied**
   - Stud services filtered from seller counts
   - Rescues excluded from license requirements
   - Petify excluded from seller analysis

4. **Spot-check top sellers**
   - Pick 2-3 from top 10, verify URLs exist
   - Confirm they're actual breeders (multiple dogs, not same litter)

5. **Verify deck renders correctly**
   - Run local server: `python3 -m http.server 8000`
   - Check all slides have data (no blank values)
   - Export PDF and verify page count

## Common Issues and Fixes

### "Since J" appearing in seller names
**Cause**: Petify scraper parsing "Member since January" as seller name
**Fix**: Exclude Petify from seller analysis in canonical_metrics.py

### Preloved showing 0% license compliance
**Cause**: Looking at `license_num` field which Preloved doesn't use
**Fix**: Map `user_type='Licensed Breeder'` to license_num

### Val (stud services) in top sellers
**Cause**: Stud filter not applied or not working
**Fix**: Verify stud_pattern regex catches all variations

### Rescues counted as needing licenses
**Cause**: Rescue organizations included in license compliance calculation
**Fix**: Identify and exclude rescues from denominator

### PDF export hangs or produces wrong output
**Cause**: Reveal.js transitions or timing issues
**Fix**: Disable transitions before capture, add small delays

## Dependencies

```bash
# Core
pip install pandas jinja2

# Scraping
pip install playwright beautifulsoup4 requests
playwright install chromium

# PDF export
pip install pillow
```

## Git Workflow

```bash
# After any data regeneration
git add canonical_metrics.json gumtree_deck/index.html gumtree_deck/deck.pdf
git commit -m "Regenerate canonical metrics and deck"
git push
```

## Future Extensibility

For new verticals (motors, property, jobs):
1. Create new scrapers for relevant platforms
2. Adapt `canonical_metrics.py` for vertical-specific fields
3. Copy `gumtree_deck/templates/` and customize slides
4. Reuse same CSS theme and build pipeline
