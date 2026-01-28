# Charity Deck Build Audit

## 1. Pipeline Map

```
Input/Raw CSVs/                    # 10 platform CSV files
        ↓
pipeline/pipeline_01_build_facts.py
        ↓
output/facts/facts.csv             # Normalized facts table (19,378 rows)
        ↓
pipeline/pipeline_02_build_derived.py
        ↓
output/views/derived.csv           # Enriched view (19,378 rows)
        ↓
canonical_metrics.py               # Computes all metrics
        ↓
canonical_metrics.json             # Single source of truth
        ↓
charity_deck/build_deck.py         # Renders template
        ↓
charity_deck/index.html            # Generated presentation
        ↓
charity_deck/scripts/export_pdf.py # Screenshot-based PDF export
        ↓
charity_deck/deck.pdf              # Final output (17 pages)
```

---

## 2. Data Source Verification

### Source CSV → derived.csv Row Counts

| Platform | Source CSV | Raw Rows | In derived.csv | Notes |
|----------|-----------|----------|----------------|-------|
| Pets4Homes | `pets4homes_v7_complete copy.csv` | 97,630 | 7,621 | Multi-scrape deduped |
| FreeAds | `freeads_enriched_COMPLETE copy.csv` | 42,907 | 6,561 | Multi-scrape deduped |
| Gumtree | `gumtree_final copy.csv` | 1,776 | 1,775 | -1 header |
| Preloved | `preloved_enriched copy.csv` | 679 | 678 | -1 header |
| ForeverPuppy | `foreverpuppy_FINAL copy.csv` | 637 | 636 | -1 header |
| Petify | `petify_data_v2.csv` | 604 | 603 | -1 header |
| Puppies | `puppies_final copy.csv` | 5,640 | 575 | Filtered duplicates |
| Kennel Club | `kc_data_PERFECT copy.csv` | 412 | 411 | -1 header |
| Gundogs Direct | `gundogs_direct_data.csv` | 363 | 356 | -1 header + filtering |
| Champdogs | `champdogs_complete copy.csv` | 864 | 162 | Litters not listings |

**Total in derived.csv:** 19,378 rows

### Unique Puppies Calculation (59,146)

```
Step 1: Start with derived.csv                    19,378 rows
Step 2: Remove non-sale items (stud/lost/merch)   -61 rows
        → raw_listings                            19,317 rows

Step 3: Compute raw puppies (listings × avg/listing)
        → raw_puppies                             62,310 dogs

Step 4: Remove duplicates
        - Within-platform (same URL)              -65 listings
        - Cross-platform (breed+loc+price)        -303 listings
        - Stale (>180 days old)                   -569 listings
        → unique_listings                         18,380 listings

Step 5: Subtract puppies from removed listings
        → unique_puppies                          59,146 dogs ✓
```

### Annualization Formula

```
annualized = unique_puppies × (365/29) × 1.2
           = 59,146 × 12.586 × 1.2
           = 893,308 dogs/year

market_share = 893,308 / 946,000 × 100 = 94.43%
```

---

## 3. Build Instructions

### Prerequisites

```bash
# Python 3.10+
pip install pandas jinja2 playwright pillow

# Browser for PDF export
playwright install chromium
```

### Full Rebuild from Scratch

```bash
cd /Users/kimfaura/Desktop/Dog_Market_Clean

# Step 1: Run pipeline (Raw CSVs → derived.csv)
python pipeline/run_pipeline.py

# Step 2: Generate metrics JSON
python canonical_metrics.py

# Step 3: Build presentation HTML
python charity_deck/build_deck.py

# Step 4: Export PDF
cd charity_deck && python scripts/export_pdf.py
```

### Verification Checklist

```bash
# Verify derived.csv row count
wc -l output/views/derived.csv
# Expected: 19404 (19378 data + 1 header + padding)

# Verify canonical_metrics.json key values
python -c "import json; m=json.load(open('canonical_metrics.json')); print(m['summary'])"
# Expected:
#   raw_listings: 19317
#   unique_puppies: 59146
#   annualized_puppies: 893308
#   market_share_pct: 94.43

# Verify deck build
python charity_deck/build_deck.py
# Expected output:
#   - 59,146 unique puppies
#   - 10 platforms
#   - 155 high-volume sellers
#   - 29.7% licensed

# Verify PDF
ls -la charity_deck/deck.pdf
# Expected: 17 pages, ~2.9 MB
```

---

## 4. Gaps & Hardcoded Values

### ⚠️ Hardcoded in Template (index.html.j2)

| Line | Value | Issue |
|------|-------|-------|
| 278, 287 | `946k/year` | UK market estimate from Naturewatch |
| 529 | `pop. 35k` | Wisbech population |
| 529 | `Ritchie — 11 listings, Bulldogs, P4H (licensed)` | Specific seller details |
| 529 | `justdogz — 9 listings, Cockapoos, FreeAds` | Specific seller details |
| 529 | `Zoe — 5 listings, Mixed, P4H (licensed)` | Specific seller details |

**Recommendation:** Move hotspot seller details to `canonical_metrics.json` under `geography.hotspot.top_sellers`.

### ⚠️ Hardcoded in canonical_metrics.py

| Line | Value | Issue |
|------|-------|-------|
| 42, 426 | `946000` | UK market estimate |
| 396 | `180` | Stale threshold (days) |
| 732 | `'Wisbech'` | Hotspot city name |

**Recommendation:** Move to config file or constants at top of file.

### ✓ Correctly Dynamic

- All platform counts, puppies, shares
- License rates and high-volume seller counts
- Freshness distributions
- Age distributions
- 8-week regulation stats
- Breed rankings
- Geographic rankings

---

## 5. Rebuild Checklist

```
□ 1. Verify raw CSVs exist in Input/Raw CSVs/
     □ pets4homes_v7_complete copy.csv
     □ freeads_enriched_COMPLETE copy.csv
     □ gumtree_final copy.csv
     □ preloved_enriched copy.csv
     □ foreverpuppy_FINAL copy.csv
     □ petify_data_v2.csv
     □ puppies_final copy.csv
     □ kc_data_PERFECT copy.csv
     □ gundogs_direct_data.csv
     □ champdogs_complete copy.csv

□ 2. Run pipeline
     □ python pipeline/run_pipeline.py
     □ Verify output/views/derived.csv exists (~11 MB)

□ 3. Generate metrics
     □ python canonical_metrics.py
     □ Verify canonical_metrics.json exists
     □ Check unique_puppies = 59,146

□ 4. Build deck
     □ python charity_deck/build_deck.py
     □ Verify charity_deck/index.html exists
     □ Preview at http://localhost:8000

□ 5. Export PDF
     □ cd charity_deck && python scripts/export_pdf.py
     □ Verify deck.pdf has 17 pages
     □ Spot-check: Slide 6 shows "59k" and "94%"

□ 6. Commit (if satisfied)
     □ git add canonical_metrics.json charity_deck/index.html charity_deck/deck.pdf
     □ git commit -m "Rebuild charity deck with latest data"
```

---

## 6. File Inventory

```
charity_deck/
├── templates/
│   └── index.html.j2          # Jinja2 template (580 lines)
├── scripts/
│   └── export_pdf.py          # PDF exporter (126 lines)
├── vendor/
│   └── dist/reveal.js         # Reveal.js library
├── build_deck.py              # Build script (207 lines)
├── theme.css                  # Slide styling
├── index.html                 # GENERATED - do not edit
├── deck.pdf                   # GENERATED - 17 pages
├── README.md                  # Usage docs
└── BUILD_AUDIT.md             # This file
```

---

## 7. Known Limitations

1. **Seller identification:** Petify only has initials, excluded from seller analysis
2. **Age data coverage:** Puppies.co.uk has <10% age data, excluded from age slide
3. **License tracking:** Only Pets4Homes and Preloved have license fields
4. **Freshness:** Champdogs and Kennel Club don't have listing dates

---

*Audit completed: January 2026*
