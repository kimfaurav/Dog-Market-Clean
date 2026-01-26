# UK Dog Market Intelligence

Analysis of ~19,000 dog listings across 10 UK platforms, representing ~59,000 dogs for sale.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Full rebuild
python pipeline/run_pipeline.py           # Raw CSVs → derived.csv
python canonical_metrics.py               # derived.csv → canonical_metrics.json
python gumtree_deck/build_deck.py         # Render presentation
python gumtree_deck/scripts/export_pdf.py # Export to PDF
```

## Project Structure

```
Dog_Market_Clean/
├── Input/Raw CSVs/           # Source data (10 platform CSVs)
├── output/
│   ├── facts/facts.csv       # Normalized facts table
│   └── views/derived.csv     # Enriched analysis view
├── pipeline/                 # ETL pipeline
│   ├── run_pipeline.py       # Master runner
│   ├── pipeline_01_build_facts.py
│   ├── pipeline_02_build_derived.py
│   └── pipeline_03_build_summary.py
├── scrapers/                 # Platform scrapers
│   ├── petify_scraper.py
│   ├── gundogs_direct_scraper.py
│   └── qa_scraper_output.py
├── gumtree_deck/             # Presentation deck
│   ├── templates/index.html.j2  # Jinja2 template
│   ├── build_deck.py            # Template renderer
│   ├── index.html               # Generated output
│   ├── deck.pdf                 # PDF export
│   └── scripts/export_pdf.py
├── canonical_metrics.py      # Generates metrics JSON
├── canonical_metrics.json    # Single source of truth
├── PROCESS.md                # Detailed process documentation
├── requirements.txt          # Python dependencies
└── _archive/                 # Historical files
```

## Data Pipeline

```
Input/Raw CSVs/  →  pipeline/  →  output/views/derived.csv
                                          ↓
                               canonical_metrics.py
                                          ↓
                               canonical_metrics.json
                                          ↓
                               gumtree_deck/build_deck.py
                                          ↓
                               gumtree_deck/index.html + deck.pdf
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

## Documentation

- **[PROCESS.md](PROCESS.md)** - Detailed process guide with platform quirks, data quality notes, and validation checklist
- **[gumtree_deck/README.md](gumtree_deck/README.md)** - Presentation build guide
- **[pipeline/README.md](pipeline/README.md)** - Pipeline documentation

## Regenerating Outputs

All metrics flow from `canonical_metrics.json`. See [PROCESS.md](PROCESS.md) for the complete rebuild process and validation steps.
