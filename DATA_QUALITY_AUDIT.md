# Data Quality Audit Report

Comprehensive audit of all 10 platform CSVs in `Input/Raw CSVs/`.

## Summary Table

| Platform | Rows | Cols | Lowest Fill Rate | Garbage Found | Duplicates | Quality Score |
|----------|------|------|------------------|---------------|------------|---------------|
| pets4homes | 7,621 | 35 | 0.1% (company_name) | 557 | 20 | **B** |
| freeads | 6,561 | 37 | 0.6% (puppy_contract) | 243 | 748 | **C** |
| gumtree | 1,775 | 18 | 99.8% (microchipped) | 1,379 | 88 | **C** |
| preloved | 678 | 19 | 3.2% (membership_level) | 1 | 2 | **A** |
| foreverpuppy | 636 | 20 | 0.0% (reposted) | 8 | 1 | **A** |
| petify | 603 | 25 | 0.0% (views) | 0 | 0 | **A** |
| puppies | 575 | 26 | 1.0% (ready_to_leave) | 34 | 2 | **B** |
| kennel_club | 411 | 23 | 8.0% (parents_health_standard) | 0 | 11 | **B** |
| gundogs_direct | 356 | 32 | 0.0% (ad_id) | 0 | 40 | **B** |
| champdogs | 162 | 30 | 0.0% (kennel_name) | 0 | 189 | **C** |

**Quality Score Legend:**
- **A** = Excellent (>80% core fill, <10 garbage, <5 dups)
- **B** = Good (some low-fill optional columns, minor issues)
- **C** = Acceptable (has known issues, usable with caveats)
- **D** = Poor (critical issues needing fix)
- **F** = Unusable

---

## Critical Issues

### 1. GUMTREE: Maintenance Page Titles (CRITICAL)

**Issue:** 1,379 of 1,775 rows (78%) have titles containing maintenance page text.

**Example:**
```
"Our site will be temporarily unavailable between 01:00 and 04:00 on the 21st..."
```

**Impact:** Title field is corrupted for majority of listings.

**Mitigation:** Pipeline uses `description` field as fallback. Derived.csv has correct titles.

**Recommendation:** Re-scrape outside maintenance window (avoid 01:00-04:00 GMT).

---

### 2. FREEADS: High Duplicate Count

**Issue:** 748 duplicate entries detected (URL duplicates + title+price+location combos).

**Impact:** Inflated listing counts.

**Mitigation:** Pipeline deduplication handles this.

**Recommendation:** Review scraper for pagination/retry logic that may cause duplicates.

---

### 3. FREEADS: Many Low Fill Rate Columns

**Issue:** 26 of 37 columns have <80% fill rate.

**Low fill columns:**
- sex: 61.1%
- color: 55.2%
- age/puppy_age: 37.9%
- Health indicators: 3-38%
- Parent info: 3-18%

**Impact:** Limited data for analysis on optional fields.

**Cause:** FreeAds listings don't consistently include structured data.

**Recommendation:** Accept as platform limitation. Core fields (url, breed, price, location) are 95%+.

---

### 4. CHAMPDOGS: Sparse Data (Limited Scraper Access)

**Issue:** 19 of 30 columns have 0% fill rate.

**Empty columns:** kennel_name, county, date_available, puppies_available, males_available, females_available, health_tests, vet_checked, assured_breeder, description, image_url

**Cause:** Detail pages require login; scraper only extracts card data.

**Impact:** Limited analysis capability.

**Recommendation:** Accept limitation or implement authenticated scraping.

---

### 5. GUNDOGS DIRECT: Template Title Issue

**Issue:** All titles are the same: "🐶 Buyer's Checklist for Gun Dogs"

**Impact:** Title field is useless for this platform.

**Cause:** Scraper extracting wrong element.

**Recommendation:** Fix scraper to extract actual listing title.

---

### 6. PETIFY: Seller Names are Initials Only

**Issue:** seller_name contains only partial names like "Since M", "Since A".

**Example:**
```
seller_name: "Since M"
seller_name: "Since A"
```

**Impact:** Cannot identify unique sellers accurately.

**Cause:** Platform displays only initials publicly.

**Recommendation:** Accept as platform limitation. Petify excluded from seller analysis.

---

## Platform-by-Platform Details

### Pets4Homes (Quality: B)

**Strengths:**
- ✅ 100% fill on all core fields
- ✅ Clean price format (numeric)
- ✅ Standardized breed names
- ✅ License tracking (11.3% have license data)

**Weaknesses:**
- ⚠️ company_name 0.1% fill (expected - most are individuals)
- ⚠️ kc_license only 1.3% fill
- ⚠️ 557 "maintenance" pattern matches (false positives in titles with numbers)

**Verdict:** High quality. Low-fill columns are optional/expected.

---

### FreeAds (Quality: C)

**Strengths:**
- ✅ Core fields 95%+ fill
- ✅ 37 columns of data
- ✅ Clean URLs

**Weaknesses:**
- ⚠️ 748 duplicates
- ⚠️ Many optional fields sparse
- ⚠️ 1 truncated image URL

**Verdict:** Usable but needs deduplication. Optional fields unreliable.

---

### Gumtree (Quality: C)

**Strengths:**
- ✅ 99.8% fill on health indicators
- ✅ Clean structured data
- ✅ No URL issues

**Weaknesses:**
- ❌ 78% titles corrupted by maintenance page
- ⚠️ 88 duplicate combos

**Verdict:** Data is good except title field. Pipeline handles this.

---

### Preloved (Quality: A)

**Strengths:**
- ✅ 80%+ fill on most fields
- ✅ Clean data
- ✅ Only 2 duplicates
- ✅ No garbage detected

**Weaknesses:**
- ⚠️ vaccinations 70.5%, health_checks 63.6%
- ⚠️ membership_level 3.2% (expected - premium feature)

**Verdict:** Excellent quality.

---

### ForeverPuppy (Quality: A)

**Strengths:**
- ✅ Core fields complete
- ✅ Health indicators 100%
- ✅ Only 1 duplicate

**Weaknesses:**
- ⚠️ 8 HTML entities (&amp;) in titles
- ⚠️ location 79.9%
- ⚠️ reposted 0% (field not populated)

**Verdict:** Good quality. Minor HTML entity issue.

---

### Petify (Quality: A)

**Strengths:**
- ✅ 100% fill on health indicators
- ✅ Zero garbage
- ✅ Zero duplicates
- ✅ Clean structured data

**Weaknesses:**
- ⚠️ Seller names are initials only
- ⚠️ date_of_birth 0.2%, views 0%

**Verdict:** Excellent quality. Seller limitation noted.

---

### Puppies.co.uk (Quality: B)

**Strengths:**
- ✅ Core fields 99%+
- ✅ Clean URLs
- ✅ Low duplicates

**Weaknesses:**
- ⚠️ Health fields 12-52% fill
- ⚠️ ready_to_leave 1%, date_of_birth 8.2%
- ⚠️ 34 false positive "maintenance" matches

**Verdict:** Good core data, sparse optional fields.

---

### Kennel Club (Quality: B)

**Strengths:**
- ✅ Breed standardized (KC format)
- ✅ 100% breeder name
- ✅ Sire/dam info complete
- ✅ Clean data

**Weaknesses:**
- ⚠️ price 60.1% (many don't list price)
- ⚠️ Health testing fields 8-23%
- ⚠️ license_number 9.7%

**Verdict:** Good quality. Price omission is common on KC.

---

### Gundogs Direct (Quality: B)

**Strengths:**
- ✅ Health indicators 100%
- ✅ Core fields complete
- ✅ Clean structured data

**Weaknesses:**
- ❌ Title is template text, not actual title
- ⚠️ Many optional fields 0-4%
- ⚠️ 40 duplicate combos

**Verdict:** Usable but title field needs fixing.

---

### Champdogs (Quality: C)

**Strengths:**
- ✅ breed, date_born 100%
- ✅ health_tested 95.7%
- ✅ Clean URLs

**Weaknesses:**
- ❌ 19 columns at 0% (login-required data)
- ⚠️ price only 6.2%
- ⚠️ 189 duplicates (breeder_url + image_url)

**Verdict:** Limited data due to login wall. Litter-based, not puppy-based.

---

## Data Consistency Notes

### Price Formats
| Platform | Format | Example |
|----------|--------|---------|
| pets4homes | £X,XXX | £1,250 |
| freeads | £X,XXX | £600 |
| gumtree | £XXX | £800 |
| preloved | £XXX | £650 |
| foreverpuppy | £X,XXX | £2,000 |
| petify | XXXX (no £) | 650 |
| puppies | £X,XXX | £1,500 |
| kennel_club | £X,XXX.XX | £2,500.00 |
| gundogs_direct | XXXX.X (float) | 350.0 |
| champdogs | Mixed/missing | - |

**Note:** Pipeline normalizes all prices to numeric.

### Breed Standardization
| Platform | Format | Example |
|----------|--------|---------|
| pets4homes | Title Case | "French Bulldog" |
| freeads | Title Case | "French Bulldog" |
| gumtree | Title Case | "French Bulldog" |
| preloved | Mixed | "French bulldog" |
| foreverpuppy | KC Style | "Dachshund Miniature Smooth Haired" |
| petify | Title Case | "French Bulldog" |
| puppies | KC Style | "Dachshund Miniature Smooth Haired" |
| kennel_club | KC Official | "Retriever (Labrador)" |
| gundogs_direct | Plural | "Cocker Spaniels" |
| champdogs | Title Case | "Labrador Retriever" |

**Note:** Pipeline normalizes breeds using mapping table.

### Date Formats
| Platform | Format | Example |
|----------|--------|---------|
| pets4homes | ISO | 2025-12-19 |
| freeads | Relative | "6 days ago" |
| gumtree | Relative | "8 days ago" |
| preloved | ISO | - |
| foreverpuppy | ISO | - |
| petify | Full | "April 17, 2025" |
| puppies | UK | "22 Dec 2025" |
| kennel_club | UK Full | "01 November 2025" |
| gundogs_direct | UK | "15 Dec 2025" |
| champdogs | UK Ordinal | "18th December 2025" |

---

## Recommendations

### Immediate Fixes Needed

1. **Gundogs Direct scraper** - Fix title extraction (currently returning template)
2. **FreeAds** - Add deduplication logic to scraper

### Re-scrape Candidates

1. **Gumtree** - Re-scrape outside maintenance window to fix titles
2. **Champdogs** - Consider authenticated scraping for full data

### Accept as Platform Limitations

1. **Petify** - Initials-only seller names (platform design)
2. **Champdogs** - Login-required detail pages
3. **Kennel Club** - Often no price listed (common practice)
4. **FreeAds** - Sparse optional fields (listing quality varies)

---

## Verification Commands

```bash
# Quick row counts
wc -l "Input/Raw CSVs/"*.csv

# Check for truncated URLs
grep -c '^[^h]' "Input/Raw CSVs/"*csv

# Count maintenance page issues in Gumtree
grep -c "temporarily unavailable" "Input/Raw CSVs/gumtree_final copy.csv"

# Check duplicates
python3 -c "
import pandas as pd
df = pd.read_csv('Input/Raw CSVs/freeads_enriched_COMPLETE copy.csv')
print(f'URL dups: {df.duplicated(subset=[\"url\"]).sum()}')
"
```

---

*Audit completed: January 2026*
