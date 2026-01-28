# UK Dog Market Intelligence

Analysis of ~19,000 dog listings across 10 UK platforms, representing ~59,000 dogs for sale.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Full rebuild (both decks)
python pipeline/run_pipeline.py             # Raw CSVs → derived.csv
python canonical_metrics.py                 # derived.csv → canonical_metrics.json
python gumtree_deck/build_deck.py           # Gumtree deck HTML
python gumtree_deck/scripts/export_pdf.py   # Gumtree deck PDF
python charity_deck/build_deck.py           # Charity deck HTML
python charity_deck/scripts/export_pdf.py   # Charity deck PDF
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
│   ├── gumtree_url_collector.py   # Gumtree Phase 1: URL collection
│   ├── gumtree_scraper.py         # Gumtree Phase 2: Enrichment
│   ├── gundogs_direct_scraper.py
│   ├── petify_scraper.py
│   └── qa_scraper_output.py
├── gumtree_deck/             # Deck for Gumtree (company pitch)
│   ├── templates/index.html.j2
│   ├── build_deck.py
│   ├── index.html
│   └── deck.pdf
├── charity_deck/             # Deck for animal welfare charities
│   ├── templates/index.html.j2
│   ├── build_deck.py
│   ├── index.html
│   └── deck.pdf
├── canonical_metrics.py      # Generates metrics JSON
├── canonical_metrics.json    # Single source of truth for BOTH decks
├── PROCESS.md                # Detailed process documentation
├── GUMTREE_AUDIT.md          # Gumtree scraping workstream audit
├── requirements.txt          # Python dependencies
└── _archive/                 # Historical files
```

## Data Pipeline

```
Input/Raw CSVs/  →  pipeline/  →  output/views/derived.csv
(10 platforms)                            ↓
                               canonical_metrics.py
                                          ↓
                               canonical_metrics.json
                                    ↓           ↓
                           gumtree_deck/    charity_deck/
                           build_deck.py    build_deck.py
                                ↓                ↓
                            deck.pdf         deck.pdf
```

Both decks use the **same data source** (`canonical_metrics.json`) covering all 10 platforms.

## Two Presentation Decks

| Deck | Audience | Slides | Purpose |
|------|----------|--------|---------|
| `gumtree_deck/` | Gumtree (company) | 19 | "Supply-Side Intelligence Engine" - pitch showing Gumtree what they could build |
| `charity_deck/` | Animal charities | 17 | Market intelligence for puppy welfare advocacy |

### Build Both Decks

```bash
# Generate shared data
python canonical_metrics.py

# Build Gumtree deck
python gumtree_deck/build_deck.py
python gumtree_deck/scripts/export_pdf.py

# Build Charity deck
python charity_deck/build_deck.py
python charity_deck/scripts/export_pdf.py
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
- **[GUMTREE_AUDIT.md](GUMTREE_AUDIT.md)** - Gumtree scraping workstream audit (URL collection + enrichment)
- **[gumtree_deck/README.md](gumtree_deck/README.md)** - Gumtree deck build guide
- **[charity_deck/BUILD_AUDIT.md](charity_deck/BUILD_AUDIT.md)** - Charity deck build audit
- **[pipeline/README.md](pipeline/README.md)** - Pipeline documentation

## Refreshing Platform Data

Each platform has its own CSV in `Input/Raw CSVs/`. To refresh a platform:

1. Run the scraper (if available in `scrapers/`)
2. Copy output to `Input/Raw CSVs/` with the expected filename
3. Run the pipeline: `python pipeline/run_pipeline.py`
4. Regenerate metrics: `python canonical_metrics.py`
5. Rebuild decks: `python gumtree_deck/build_deck.py && python charity_deck/build_deck.py`

See [GUMTREE_AUDIT.md](GUMTREE_AUDIT.md) for the complete Gumtree two-phase scrape procedure.

## Regenerating Outputs

All metrics flow from `canonical_metrics.json`. See [PROCESS.md](PROCESS.md) for the complete rebuild process and validation steps.
