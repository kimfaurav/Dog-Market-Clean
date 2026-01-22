# Data Extraction Changes Log

## Recent Changes (Jan 22, 2026)

### Kennel Club Litter Size Extraction
**File**: [pipeline/pipeline_01_build_facts.py](pipeline_01_build_facts.py)

**Problem Identified**: 
- Kennel Club raw CSV contained `litter_size` field with detailed "X Bitch, Y Dog" format
- Field was 100% populated (411 listings) but NOT being extracted
- 0 puppy counts were being saved for Kennel Club data

**Solution Implemented**:
1. Added `parse_kennel_club_litter_size()` function (lines 25-54)
   - Parses "2 Bitch, 3 Dog" → 5 puppies
   - Uses regex to extract and sum male + female counts
   
2. Modified `load_platform_data()` function (lines 308-310)
   - Applied parser to kennel_club data during load
   - Converts text format to numeric before mapping

3. Updated PLATFORM_CONFIG mapping (line 176)
   - Added `"litter_size": "total_available"` to kennel_club config

**Results**:
- Kennel Club: 411 listings → 2,453 puppies extracted
- Previously: 411 listings → 0 puppies
- Coverage: 100% (all Kennel Club listings now have puppy counts)
- Distribution: Min=1, Max=12 puppies per litter (realistic)

**Why This Matters**:
- Avoided losing ~2,400 data points
- Increased data quality for authoritative breeding registry
- Demonstrated importance of checking raw CSV fields before assuming they're unavailable

---

## Field Mapping Audit Status

### Puppy Count Fields by Platform

| Platform | Raw Field | Mapping Status | Notes |
|----------|-----------|----------------|-------|
| pets4homes | `total_available` | ✅ Extracted | Direct field |
| foreverpuppy | `total_available` | ✅ Extracted | Direct field |
| petify | `males_available`, `females_available` | ✅ Extracted | Combined by pipeline_02 |
| kennel_club | `litter_size` | ✅ Extracted (Jan 22) | Parse "X Bitch, Y Dog" |
| champdogs | `puppies_available` | ❌ NULL in scrape | Field exists but not populated |
| gumtree | None | N/A | No field in raw CSV |
| freeads | None | N/A | No field in raw CSV |
| preloved | None | N/A | No field in raw CSV |
| puppies | None | N/A | No field in raw CSV |

### Unmapped Fields Available in Raw CSVs

**Champdogs** (worth investigating):
- Has `males_available` and `females_available` fields
- Could combine these like petify does
- Current `puppies_available` field is NULL, but gender split might work

---

## Validation & Quality Checks

### Implemented (in pipeline_02):
- ✅ `validate_puppy_counts()` function catches:
  - Values > 20 (likely parsing errors)
  - Year-like values (1800-2099 parsed as counts)
  - Prices > £500 parsed as counts
  - Result: 22 suspicious freeads entries flagged and corrected

### Available Analysis Scripts:
- `check_puppy_count.py` - Platform-by-platform puppy count verification
- `improved_extraction.py` - Shows potential gains from title parsing
- `confidence_all_platforms.py` - Confidence ratings by platform
- `comprehensive_qa_audit.py` - Full data quality audit

---

## Best Practices to Avoid Repeating Mistakes

1. **Always audit raw CSV columns before assuming missing data**
   - Check: `df.columns` and `df['field'].notna().sum()`
   - Example: Kennel Club had 411 rows of litter_size data

2. **Test parsing on sample values first**
   - Before applying pipeline-wide: test regex on 5-10 actual values
   - Verify edge cases (e.g., "1 Bitch, 1 Dog" vs "2 Bitch, 2 Dog")

3. **Document field mappings in README**
   - Pipeline README now includes table showing extraction source for each platform
   - Makes it clear what's extracted vs. what requires title parsing

4. **Validate extraction with spot checks**
   - Run analysis script after pipeline changes
   - Compare: min, max, mean, and distribution of extracted values
   - Flag unusual distributions (e.g., all values = 1 would be suspicious)

5. **Save analysis scripts with meaningful names**
   - `check_puppy_count.py` - Clear purpose and reusable
   - Keep in root for easy access during investigations

---

## Next Steps to Consider

### High Priority (data already available):
- [ ] Investigate Champdogs `males_available` + `females_available` (162 listings)
- [ ] Check if Champdogs `puppies_available` can be re-scraped

### Medium Priority (requires title parsing):
- [ ] Implement gumtree title parsing (1,775 listings)
- [ ] Implement freeads title parsing (6,561 listings)
- [ ] Pattern: "X pups", "litter of X", "X boys/X girls"
- [ ] Potential gain: 3,000-5,000 additional puppies

---

## Running the Pipeline

```bash
cd /Users/kimfaura/Desktop/Dog_Market_Clean
python3 pipeline/run_pipeline.py
```

This runs all 3 steps and updates:
- `output/facts/facts.csv` (raw field mapping)
- `output/views/derived.csv` (parsed timestamps & availability)
- `output/views/platform_supply_summary.csv` (platform summary)

To verify extraction after changes:
```bash
python3 check_puppy_count.py
```
