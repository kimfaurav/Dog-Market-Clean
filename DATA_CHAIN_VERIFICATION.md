# Data Chain Verification

Complete trace from scrapers → CSVs → pipeline → canonical metrics.

## Summary

| Check | Status |
|-------|--------|
| All 10 pipeline inputs exist | ✅ Pass |
| Row counts match (Raw → Derived) | ✅ Pass (19,378) |
| Canonical metrics generated | ✅ Pass |
| All scrapers produce correct output | ⚠️ 4 issues |

---

## 1. Pipeline Input Requirements

The pipeline (`pipeline/pipeline_01_build_facts.py`) expects these files:

| Platform | File Pattern | Matched File | Status |
|----------|--------------|--------------|--------|
| pets4homes | `pets4homes_v7_complete*.csv` | `pets4homes_v7_complete copy.csv` | ✅ Found |
| freeads | `freeads_enriched_COMPLETE*.csv` | `freeads_enriched_COMPLETE copy.csv` | ✅ Found |
| gumtree | `gumtree_final*.csv` | `gumtree_final copy.csv` | ✅ Found |
| preloved | `preloved_enriched*.csv` | `preloved_enriched copy.csv` | ✅ Found |
| foreverpuppy | `foreverpuppy_FINAL*.csv` | `foreverpuppy_FINAL copy.csv` | ✅ Found |
| petify | `petify_data*.csv` | `petify_data_v2.csv` | ✅ Found |
| puppies | `puppies_final*.csv` | `puppies_final copy.csv` | ✅ Found |
| kennel_club | `kc_data_PERFECT*.csv` | `kc_data_PERFECT copy.csv` | ✅ Found |
| gundogs_direct | `gundogs_direct_data*.csv` | `gundogs_direct_data.csv` | ✅ Found |
| champdogs | `champdogs_complete*.csv` | `champdogs_complete copy.csv` | ✅ Found |

**All 10 inputs present.**

---

## 2. Raw CSV Inventory

| Filename | Size | Modified | Rows | Columns |
|----------|------|----------|------|---------|
| pets4homes_v7_complete copy.csv | 9.4 MB | Jan 22 | 7,621 | 35 |
| freeads_enriched_COMPLETE copy.csv | 7.5 MB | Jan 22 | 6,561 | 37 |
| gumtree_final copy.csv | 1.5 MB | Jan 22 | 1,775 | 18 |
| preloved_enriched copy.csv | 189 KB | Jan 22 | 678 | 19 |
| foreverpuppy_FINAL copy.csv | 181 KB | Jan 22 | 636 | 20 |
| petify_data_v2.csv | 195 KB | Jan 24 | 603 | 25 |
| puppies_final copy.csv | 619 KB | Jan 22 | 575 | 26 |
| kc_data_PERFECT copy.csv | 189 KB | Jan 22 | 411 | 23 |
| gundogs_direct_data.csv | 125 KB | Jan 24 | 356 | 32 |
| champdogs_complete copy.csv | 64 KB | Jan 22 | 162 | 30 |
| **TOTAL** | | | **19,378** | |

**Note:** `petify_data_v3.csv` also exists (126 KB, Jan 25) but pipeline uses v2 (matched first by glob).

---

## 3. Scraper → CSV Mapping

| Platform | Scraper | Output Filename | Pipeline Expects | Match? |
|----------|---------|-----------------|------------------|--------|
| pets4homes | `pets4homes_scraper.py` | `pets4homes_v6_complete.csv` | `pets4homes_v7_complete*.csv` | ⚠️ Version mismatch |
| freeads | `freeads_scraper.py` | `freeads_enriched_COMPLETE.csv` | `freeads_enriched_COMPLETE*.csv` | ✅ Match |
| gumtree | `gumtree_scraper.py` | `gumtree_ENRICHED.csv` | `gumtree_final*.csv` | ⚠️ Name mismatch |
| preloved | `preloved_scraper.py` | `preloved_enriched.csv` | `preloved_enriched*.csv` | ✅ Match |
| foreverpuppy | `foreverpuppy_scraper.py` | JSON output | `foreverpuppy_FINAL*.csv` | ⚠️ No CSV output |
| petify | `petify_scraper.py` | `petify_data_v3.csv` | `petify_data*.csv` | ✅ Match |
| puppies | `puppies_scraper.py` | `puppies_{timestamp}.csv` | `puppies_final*.csv` | ⚠️ Name mismatch |
| kennel_club | `kennel_club_scraper.py` | `kc_data.csv` variants | `kc_data_PERFECT*.csv` | ⚠️ Name mismatch |
| gundogs_direct | `gundogs_direct_scraper.py` | `gundogs_direct_data.csv` | `gundogs_direct_data*.csv` | ✅ Match |
| champdogs | `champdogs_scraper.py` | `champdogs_complete.csv` | `champdogs_complete*.csv` | ✅ Match |

---

## 4. Identified Gaps

### Gap 1: Gumtree Scraper Output Name
- **Scraper outputs:** `gumtree_ENRICHED.csv`
- **Pipeline expects:** `gumtree_final*.csv`
- **Current workaround:** Manual rename
- **Fix:** Rename scraper output to `gumtree_final.csv`

### Gap 2: Puppies Scraper Output Name
- **Scraper outputs:** `puppies_{timestamp}.csv`
- **Pipeline expects:** `puppies_final*.csv`
- **Current workaround:** Manual rename
- **Fix:** Rename scraper output to `puppies_final.csv`

### Gap 3: ForeverPuppy Scraper Output
- **Scraper outputs:** JSON only
- **Pipeline expects:** `foreverpuppy_FINAL*.csv`
- **Current workaround:** Unknown source for CSV
- **Fix:** Add CSV export to scraper

### Gap 4: Kennel Club Scraper Output Name
- **Scraper outputs:** Various `kc_data*.csv`
- **Pipeline expects:** `kc_data_PERFECT*.csv`
- **Current workaround:** Manual rename
- **Fix:** Rename scraper output to `kc_data_PERFECT.csv`

### Gap 5: Pets4Homes Version Mismatch
- **Scraper outputs:** `pets4homes_v6_complete.csv`
- **Pipeline expects:** `pets4homes_v7_complete*.csv`
- **Current workaround:** Manual rename
- **Fix:** Update scraper to output v7 or pipeline to accept v6

---

## 5. Complete Data Chain

```
SCRAPER LAYER
─────────────────────────────────────────────────────────────────────
Platform        Scraper(s)                     → Output
─────────────────────────────────────────────────────────────────────
pets4homes      pets4homes_scraper.py          → pets4homes_v6_complete.csv
freeads         freeads_url_collector.py +     → freeads_enriched_COMPLETE.csv
                freeads_scraper.py
gumtree         gumtree_url_collector.py +     → gumtree_ENRICHED.csv
                gumtree_scraper.py
preloved        preloved_scraper.py            → preloved_enriched.csv
foreverpuppy    foreverpuppy_scraper.py        → foreverpuppy_ALL.json
petify          petify_scraper.py              → petify_data_v3.csv
puppies         puppies_scraper.py             → puppies_{timestamp}.csv
kennel_club     kennel_club_url_collector.py + → kc_data.csv
                kennel_club_scraper.py
gundogs_direct  gundogs_direct_scraper.py      → gundogs_direct_data.csv
champdogs       champdogs_scraper.py           → champdogs_complete.csv

                              ↓ (manual rename/copy)

RAW CSV LAYER (Input/Raw CSVs/)
─────────────────────────────────────────────────────────────────────
pets4homes_v7_complete copy.csv     (7,621 rows)
freeads_enriched_COMPLETE copy.csv  (6,561 rows)
gumtree_final copy.csv              (1,775 rows)
preloved_enriched copy.csv          (678 rows)
foreverpuppy_FINAL copy.csv         (636 rows)
petify_data_v2.csv                  (603 rows)
puppies_final copy.csv              (575 rows)
kc_data_PERFECT copy.csv            (411 rows)
gundogs_direct_data.csv             (356 rows)
champdogs_complete copy.csv         (162 rows)
                                    ─────────────
                                    19,378 total

                              ↓

PIPELINE LAYER
─────────────────────────────────────────────────────────────────────
pipeline/run_pipeline.py
    ├── pipeline_01_build_facts.py  → output/facts/facts.csv
    ├── pipeline_02_build_derived.py → output/views/derived.csv
    └── pipeline_03_build_summary.py → output/views/platform_supply_summary.csv

                              ↓

DERIVED.CSV (19,378 rows, 87 columns)
─────────────────────────────────────────────────────────────────────
Platform breakdown:
  pets4homes:     7,621
  freeads:        6,561
  gumtree:        1,775
  preloved:         678
  foreverpuppy:     636
  petify:           603
  puppies:          575
  kennel_club:      411
  gundogs_direct:   356
  champdogs:        162

                              ↓

CANONICAL METRICS LAYER
─────────────────────────────────────────────────────────────────────
canonical_metrics.py
    ↓
canonical_metrics.json
    - raw_listings: 19,317 (after non-sale filter)
    - unique_puppies: 59,146 (after dedup)
    - annualized: 893,308
    - market_share: 94.43%

                              ↓

PRESENTATION LAYER
─────────────────────────────────────────────────────────────────────
gumtree_deck/build_deck.py  → gumtree_deck/index.html → deck.pdf
charity_deck/build_deck.py  → charity_deck/index.html → deck.pdf
```

---

## 6. Verification Commands

```bash
# Verify pipeline runs successfully
python pipeline/run_pipeline.py

# Verify row counts match
python3 -c "
import pandas as pd
raw_total = sum([
    len(pd.read_csv('Input/Raw CSVs/pets4homes_v7_complete copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/freeads_enriched_COMPLETE copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/gumtree_final copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/preloved_enriched copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/foreverpuppy_FINAL copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/petify_data_v2.csv')),
    len(pd.read_csv('Input/Raw CSVs/puppies_final copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/kc_data_PERFECT copy.csv')),
    len(pd.read_csv('Input/Raw CSVs/gundogs_direct_data.csv')),
    len(pd.read_csv('Input/Raw CSVs/champdogs_complete copy.csv')),
])
derived = len(pd.read_csv('output/views/derived.csv'))
print(f'Raw CSVs total: {raw_total}')
print(f'Derived.csv: {derived}')
print(f'Match: {raw_total == derived}')
"

# Verify canonical metrics
python3 -c "
import json
m = json.load(open('canonical_metrics.json'))
print(f\"Unique puppies: {m['summary']['unique_puppies']:,}\")
print(f\"Market share: {m['summary']['market_share_pct']}%\")
"
```

---

## 7. Recommendations

### Immediate Actions (filename standardization)

1. **Update `gumtree_scraper.py`** to output `gumtree_final.csv` instead of `gumtree_ENRICHED.csv`

2. **Update `puppies_scraper.py`** to output `puppies_final.csv` instead of timestamped filename

3. **Add CSV export to `foreverpuppy_scraper.py`** and name it `foreverpuppy_FINAL.csv`

4. **Update KC scraper chain** to produce `kc_data_PERFECT.csv`

5. **Update `pets4homes_scraper.py`** to output v7 filename or update pipeline to accept v6

### Alternative: Update Pipeline Patterns

Instead of changing scrapers, update `pipeline_01_build_facts.py` PLATFORM_CONFIG patterns:
- `gumtree_final*.csv` → `gumtree*.csv`
- `puppies_final*.csv` → `puppies*.csv`
- etc.

### Documentation

All CSVs should be renamed when copied to `Input/Raw CSVs/` to match pipeline expectations. Document this in PROCESS.md.

---

*Verification completed: January 2026*
