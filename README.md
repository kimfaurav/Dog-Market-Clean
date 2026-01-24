# UK Dog Market Analysis

Analysis of ~19,000 dog listings across 9 UK platforms, representing ~62,000 dogs for sale.

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
├── Input/Raw CSVs/           # Source data (9 platform CSVs)
├── output/
│   ├── facts/facts.csv       # Normalized facts table
│   └── views/derived.csv     # Enriched analysis view
├── pipeline/                 # ETL pipeline scripts
│   ├── run_pipeline.py       # Master runner
│   ├── pipeline_01_build_facts.py
│   ├── pipeline_02_build_derived.py
│   └── pipeline_03_build_summary.py
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

## Platforms Covered

| Platform | Listings | Dogs | Share |
|----------|----------|------|-------|
| Pets4Homes | 7,617 | 31,312 | 50.6% |
| FreeAds | 6,551 | 14,258 | 23.0% |
| Gumtree | 1,758 | 4,450 | 7.2% |
| Petify | 603 | 3,315 | 5.4% |
| ForeverPuppy | 630 | 2,529 | 4.1% |
| Kennel Club | 411 | 2,453 | 4.0% |
| Puppies.co.uk | 575 | 1,750 | 2.8% |
| Champdogs | 162 | 972 | 1.6% |
| Preloved | 654 | 893 | 1.4% |

## Key Metrics

- **Total listings:** 18,961
- **Total dogs:** 61,932
- **Unique sellers:** 17,304
- **Annualized estimate:** 889,275 dogs/year
- **Market share:** 94% of UK dog sales

## Regenerating Outputs

All metrics flow from `canonical_metrics.json`. To update:

1. Modify source CSVs in `Input/Raw CSVs/`
2. Run `python pipeline/run_pipeline.py`
3. Run `python canonical_metrics.py`
4. Slides will reflect new metrics

## Archive

Historical analysis scripts and documentation are preserved in `_archive/`.
