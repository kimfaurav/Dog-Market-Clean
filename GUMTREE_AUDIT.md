# Gumtree Scraping Workstream Audit

## 1. Canonical Files Identification

### Canonical CSV
```
Input/Raw CSVs/gumtree_final copy.csv
```
- **Rows**: 1,775 (+ 1 header = 1,776 lines)
- **Last modified**: Jan 22, 2024
- **Status**: ✅ DEFINITIVE - Used by pipeline

### Gold Scraper
```
scrapers/gumtree_scraper.py
```
- **Source**: Recovered from `/Users/kimfaura/Desktop/Pets/Gumtree/gumtree_enrichment_PERFECT.py`
- **Framework**: Playwright (matches project pattern)
- **Status**: ✅ RECOVERED AND INSTALLED

---

## 2. Scraper Documentation

### Overview

The gold scraper (`gumtree_scraper.py`) is a two-phase system:
1. **Phase 1**: Collect listing URLs (requires separate URL collection script)
2. **Phase 2**: Enrich each URL with full listing details

### Dependencies

```bash
pip install playwright
playwright install chromium
```

### Input Requirements

The scraper expects a text file with Gumtree listing URLs:
```
gumtree_urls.txt (one URL per line)
```

Example:
```
https://www.gumtree.com/p/dogs/french-bulldog-puppies/1508123456
https://www.gumtree.com/p/dogs/labrador-retriever-pups/1508234567
...
```

### How to Run

```bash
cd /Users/kimfaura/Desktop/Dog_Market_Clean/scrapers

# Basic usage (uses default filenames)
python gumtree_scraper.py gumtree_urls.txt gumtree_output.json

# Or with defaults
python gumtree_scraper.py
# Expects: gumtree_urls.txt → outputs: gumtree_ENRICHED.json + .csv
```

### Output Format

**CSV columns** (matches canonical):
```
url, ad_id, title, price, location, breed, sex, age_detail,
ready_to_leave, microchipped, vaccinated, kc_registered,
health_checked, neutered, deflead, seller_name, posted, description
```

### Key Features

1. **SVG Color Detection**: Uses `#028546` (green checkmark) to detect Yes/No badges
2. **Resumable**: Saves progress every 25 listings to JSON
3. **Human-like Delays**: 2-4 second random delays between requests
4. **Cookie Consent**: Auto-accepts Gumtree cookie popup
5. **Visible Browser**: Runs `headless=False` to avoid Cloudflare detection

### Known Issues / Limitations

| Issue | Workaround |
|-------|------------|
| **Cloudflare protection** | Runs visible browser (headless=False) |
| **Rate limiting** | Built-in random delays (2-4s) |
| **Maintenance pages** | Re-run on failed URLs |
| **No URL collector** | Need separate script to get listing URLs first |

---

## 3. URL Collection (Phase 1)

### Gold URL Collector
```
scrapers/gumtree_url_collector.py
```
- **Source**: Recovered from `/Users/kimfaura/Desktop/Pets/Gumtree/gumtree_ultimate.py`
- **Framework**: Playwright (visible browser)
- **Status**: ✅ RECOVERED AND INSTALLED

### How It Works

The URL collector runs in two phases:

**Phase 1a - Discovery**: Iterates through 160+ breed slugs, checking each for listing counts
```
https://www.gumtree.com/pets/pets-for-sale/dogs/{breed-slug}
```

**Phase 1b - Pagination**: For breeds with listings, paginates through all pages collecting URLs
- Scrolls page to load lazy content
- Extracts links matching `article a[href*="/p/dogs/"]`
- Uses forward pagination button `[data-q="pagination-forward-page"]`
- Stops when no new URLs found

### How to Run (Phase 1)

```bash
cd /Users/kimfaura/Desktop/Dog_Market_Clean/scrapers

# Run URL collector (takes 30-60 minutes)
python gumtree_url_collector.py

# Output files:
#   gumtree_ULTIMATE_urls.txt    - All collected URLs
#   gumtree_breed_results.json   - Per-breed coverage stats
```

### Output Format

```
gumtree_ULTIMATE_urls.txt (one URL per line):
https://www.gumtree.com/p/dogs/french-bulldog-puppies/1508123456
https://www.gumtree.com/p/dogs/labrador-retriever-pups/1508234567
...
```

### Key Features

1. **160+ Breed Slugs**: Comprehensive breed coverage
2. **Count Tracking**: Reports expected vs actual URLs per breed
3. **80% Threshold**: Flags breeds with <80% coverage
4. **Incremental Save**: Saves after each breed
5. **Visible Browser**: Runs `headless=False` to avoid Cloudflare

---

## 4. Data Flow Trace

```
PHASE 1: URL COLLECTION
scrapers/gumtree_url_collector.py
        ↓
gumtree_ULTIMATE_urls.txt (~2000+ URLs)
        ↓

PHASE 2: ENRICHMENT
scrapers/gumtree_scraper.py gumtree_ULTIMATE_urls.txt output.json
        ↓
gumtree_ENRICHED.csv (full listing details)
        ↓

PHASE 3: PIPELINE INTEGRATION
Copy to: Input/Raw CSVs/gumtree_final copy.csv
        ↓
pipeline/run_pipeline.py
        ↓
output/views/derived.csv (Gumtree rows)
        ↓
canonical_metrics.py
        ↓
canonical_metrics.json
    platforms.gumtree:
      listings: 1,758 (after non-sale filter)
      puppies: 4,450
      share: 7.1%
```

---

## 5. Current Scrapeability Test

**Tested**: January 2026

```
✓ Page loaded successfully
  Found 30 article elements
  Found 30 dog listing links
✓ SCRAPING FEASIBLE
```

**Status**: Gumtree is currently accessible. No Cloudflare challenge in headless mode (but scraper uses visible browser for safety).

---

## 6. Data Quality Analysis

### Column Fill Rates (Current Canonical)

| Column | Fill Rate | Notes |
|--------|-----------|-------|
| url | 100% (1,775) | ✅ All valid |
| ad_id | 100% (1,775) | ✅ Complete |
| title | 100% (1,775) | ⚠️ 73% have maintenance text |
| price | 100% (1,775) | ✅ Complete |
| location | 100% (1,775) | ✅ Complete |
| breed | 100% (1,775) | ✅ Complete |
| sex | 100% (1,775) | ✅ Complete |
| age_detail | 100% (1,775) | ✅ Complete |
| ready_to_leave | 100% (1,775) | ✅ Complete |
| microchipped | 99.8% (1,772) | ✅ Excellent |
| vaccinated | 99.8% (1,772) | ✅ Excellent |
| kc_registered | 99.8% (1,772) | ✅ Excellent |
| health_checked | 99.8% (1,772) | ✅ Excellent |
| neutered | 99.8% (1,772) | ✅ Excellent |
| deflead | 99.8% (1,772) | ✅ Excellent |
| seller_name | 100% (1,775) | ✅ Complete |
| posted | 100% (1,775) | ✅ Complete |
| description | 100% (1,775) | ✅ Complete |

### URL Truncation Check
```
✅ NO TRUNCATED URLs FOUND
   Full URLs (https://www.gumtree.com...): 1,775 / 1,775 (100%)
```

### Health Badge Detection
- **Method**: SVG color detection (`#028546` = green = Yes)
- **Format**: Text ("Yes"/"No")

---

## 7. Known Issues

### ⚠️ Title Field Corruption (Historical)

**Problem**: 1,303 of 1,775 rows (73%) have titles containing maintenance page text.

**Mitigation**: Pipeline uses `description` field as fallback. Derived.csv has 0 corrupted titles.

**Prevention**: Run scraper outside Gumtree maintenance windows (avoid 01:00-04:00 GMT).

### ✅ Resolved: Missing Scrapers

**Previously**: No Gumtree scrapers in project.
**Now**:
- `scrapers/gumtree_url_collector.py` - URL collection (Phase 1)
- `scrapers/gumtree_scraper.py` - Enrichment (Phase 2)

### ✅ Resolved: Truncated URLs

The "1,054 truncated URLs" issue is NOT present in current canonical file.

---

## 8. Full Re-scrape Procedure

### Complete Two-Phase Scrape from Zero

```bash
cd /Users/kimfaura/Desktop/Dog_Market_Clean/scrapers

# ============================================
# PHASE 1: URL COLLECTION (30-60 minutes)
# ============================================
python gumtree_url_collector.py

# Output:
#   gumtree_ULTIMATE_urls.txt    (~2000+ URLs)
#   gumtree_breed_results.json   (coverage stats)

# Verify URL count
wc -l gumtree_ULTIMATE_urls.txt
# Expected: 1500-2500 URLs depending on market


# ============================================
# PHASE 2: ENRICHMENT (1-2 hours)
# ============================================
python gumtree_scraper.py gumtree_ULTIMATE_urls.txt gumtree_NEW.json

# Output:
#   gumtree_NEW.json   (full data)
#   gumtree_NEW.csv    (same data, CSV format)

# Verify completion
python3 -c "import json; d=json.load(open('gumtree_NEW.json')); print(f'Total: {len(d)}, Complete: {len([x for x in d if x.get(\"seller_name\") and x.get(\"breed\")])}')"


# ============================================
# PHASE 3: PIPELINE INTEGRATION
# ============================================
cd /Users/kimfaura/Desktop/Dog_Market_Clean

# Copy output to raw CSVs folder
cp scrapers/gumtree_NEW.csv "Input/Raw CSVs/gumtree_final copy.csv"

# Run pipeline
python pipeline/run_pipeline.py

# Generate metrics
python canonical_metrics.py

# Verify
python3 -c "
import pandas as pd
df = pd.read_csv('output/views/derived.csv')
gt = df[df['platform']=='gumtree']
print(f'Gumtree rows: {len(gt)}')
print(f'Fill rates:')
for col in ['title', 'breed', 'seller_name', 'health_checked']:
    fill = gt[col].notna().sum() / len(gt) * 100
    print(f'  {col}: {fill:.1f}%')
"
```

### Quick Reference

| Phase | Script | Input | Output | Duration |
|-------|--------|-------|--------|----------|
| 1 | `gumtree_url_collector.py` | (none) | `gumtree_ULTIMATE_urls.txt` | 30-60 min |
| 2 | `gumtree_scraper.py` | URLs file | `gumtree_NEW.csv` | 1-2 hours |
| 3 | `run_pipeline.py` | CSV | `derived.csv` | 2 min |

---

## 9. Verification Checklist

```
□ 1. Scrapers exist
     □ scrapers/gumtree_url_collector.py (Phase 1)
     □ scrapers/gumtree_scraper.py (Phase 2)

□ 2. Dependencies installed
     □ pip install playwright
     □ playwright install chromium

□ 3. Test URL collector (quick check)
     □ cd scrapers && python -c "from gumtree_url_collector import BREED_SLUGS; print(f'{len(BREED_SLUGS)} breeds')"
     □ Expected: 163 breeds

□ 4. Source file exists
     □ Input/Raw CSVs/gumtree_final copy.csv (1,776 lines)

□ 5. Run pipeline
     □ python pipeline/run_pipeline.py
     □ Verify output/views/derived.csv contains Gumtree

□ 6. Check Gumtree row count
     □ Expected: 1,775 rows in derived.csv

□ 7. Check canonical_metrics.json
     □ platforms.gumtree.listings ≈ 1,758
     □ platforms.gumtree.puppies ≈ 4,450
```

---

## 10. Summary

| Metric | Status |
|--------|--------|
| Canonical CSV | ✅ `gumtree_final copy.csv` (1,775 rows) |
| URL Collector | ✅ `scrapers/gumtree_url_collector.py` (recovered) |
| Enrichment Scraper | ✅ `scrapers/gumtree_scraper.py` (recovered) |
| Scrapeability | ✅ Tested feasible (Jan 2026) |
| URL quality | ✅ 100% valid (no truncation) |
| Fill rates | ✅ 99.8-100% |
| Title issue | ⚠️ 73% corrupted in raw, mitigated by pipeline |
| Pipeline integration | ✅ Working |
| **Full Replication** | ✅ **YES - Can replicate from zero** |

**Bottom line**: Gumtree scraping workstream is now fully documented and reproducible. Both the URL collector and enrichment scraper have been recovered and installed. A complete scrape from zero is possible using the two-phase procedure in Section 8.

---

## 11. Replication Verification

**Can we replicate a full Gumtree scrape from zero?**

✅ **YES**

| Component | Status | File |
|-----------|--------|------|
| URL Collector | ✅ Recovered | `scrapers/gumtree_url_collector.py` |
| Enrichment Scraper | ✅ Recovered | `scrapers/gumtree_scraper.py` |
| Breed Coverage | ✅ 163 breeds | Embedded in URL collector |
| Dependencies | ✅ Playwright | `pip install playwright && playwright install chromium` |
| Output Format | ✅ Matches canonical | 18 columns matching pipeline expectations |

**What's needed to run:**
1. Python 3.8+
2. Playwright + Chromium
3. Visible display (both scripts use `headless=False`)

**Estimated time for full scrape:**
- Phase 1 (URL collection): 30-60 minutes
- Phase 2 (Enrichment): 1-2 hours for ~2000 URLs
- Phase 3 (Pipeline): 2 minutes

---

*Audit completed: January 2026*
*URL collector recovered from: /Users/kimfaura/Desktop/Pets/Gumtree/gumtree_ultimate.py*
*Enrichment scraper recovered from: /Users/kimfaura/Desktop/Pets/Gumtree/gumtree_enrichment_PERFECT.py*
