# UK Dog Market Analysis

Analysis of ~19,000 dog listings across 10 UK platforms, representing ~59,000 dogs for sale.

## Current Status (Jan 24, 2026)

**Latest session completed:**
- Fixed Gundogs Direct scraper (seller_name regex was broken - captured wrong field)
- Re-ran full pipeline with corrected data
- Added scraper QA validation script (`scrapers/qa_scraper_output.py`)
- Updated all slides with correct Gundogs data
- Slide refinements: compressed tables, fixed stacked bar percentages, improved text
- Generated new PDF with all changes

**Next steps / TODO:**
- Review final PDF for any remaining issues
- Consider adding more platforms if needed
- Merge metrics-tooling branch to main when ready

**Key files modified this session:**
- `scrapers/gundogs_direct_scraper.py` - fixed seller_name regex
- `scrapers/qa_scraper_output.py` - NEW: validates scraper output before pipeline
- `uk_dog_market_slide.html` - multiple slide refinements
- `canonical_metrics.json` - regenerated with correct Gundogs data

## Quick Start

```bash
# 1. Run the data pipeline (Input CSVs → derived.csv)
python pipeline/run_pipeline.py

# 2. Generate canonical metrics
python canonical_metrics.py

# 3. Generate slides (optional - updates HTML from metrics)
python generate_slides.py

# 4. Generate PDF screenshots
python screenshot_slides.py
```

## Folder Structure

```
Dog_Market_Clean/
├── Input/Raw CSVs/           # Source data (10 platform CSVs)
├── output/
│   ├── facts/facts.csv       # Normalized facts table
│   └── views/derived.csv     # Enriched analysis view
├── pipeline/                 # ETL pipeline scripts
│   ├── run_pipeline.py       # Master runner
│   ├── pipeline_01_build_facts.py
│   ├── pipeline_02_build_derived.py
│   └── pipeline_03_build_summary.py
├── scrapers/                 # Platform scrapers
│   ├── gundogs_direct_scraper.py  # Gundogs Direct scraper
│   └── qa_scraper_output.py       # QA validation for scraper output
├── canonical_metrics.py      # Generates canonical_metrics.json
├── canonical_metrics.json    # Single source of truth for all metrics
├── generate_slides.py        # Generates HTML slides
├── screenshot_slides.py      # Converts HTML to PDF
├── uk_dog_market_slide.html  # Final presentation
├── uk_dog_market_slides.pdf  # PDF export
└── slide_screenshots/        # Individual slide PNGs
```

## Data Pipeline

```
Input CSVs → pipeline_01 → facts.csv → pipeline_02 → derived.csv
                                                          ↓
                                              canonical_metrics.py
                                                          ↓
                                              canonical_metrics.json
                                                          ↓
                                              uk_dog_market_slide.html
```

## Platforms Covered (10)

| Platform | Listings | Dogs | Share |
|----------|----------|------|-------|
| Pets4Homes | 7,621 | 31,312 | 52.9% |
| FreeAds | 6,561 | 14,258 | 24.1% |
| Gumtree | 1,758 | 4,450 | 7.5% |
| Petify | 603 | 3,315 | 5.6% |
| ForeverPuppy | 636 | 2,529 | 4.3% |
| Kennel Club | 411 | 2,453 | 4.1% |
| Puppies.co.uk | 575 | 1,750 | 3.0% |
| Champdogs | 162 | 972 | 1.6% |
| Preloved | 678 | 893 | 1.5% |
| Gundogs Direct | 356 | 378 | 0.6% |

## Key Metrics

- **Total listings:** 19,317
- **Total dogs:** 59,146
- **Unique sellers:** ~17,500
- **Annualized estimate:** 893,308 dogs/year
- **Market share:** 94.4% of UK dog sales

## Regenerating Outputs

All metrics flow from `canonical_metrics.json`. To update:

1. Modify source CSVs in `Input/Raw CSVs/`
2. Run `python pipeline/run_pipeline.py`
3. Run `python canonical_metrics.py`
4. Slides will reflect new metrics

## Archive

Historical analysis scripts and documentation are preserved in `_archive/`.
