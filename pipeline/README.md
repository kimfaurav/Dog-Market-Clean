# Dog Market Pipeline - Clean Rebuild

## Overview

This is a clean, minimal pipeline for processing UK dog marketplace data across 9 platforms. It replaces the previous fragmented v2/v3 scripts with a single coherent flow.

## Pipeline Structure

```
pipeline/
├── run_pipeline.py              # Master runner (executes all steps)
├── pipeline_01_build_facts.py   # Raw CSVs → facts.csv
├── pipeline_02_build_derived.py # facts.csv → derived.csv
└── pipeline_03_build_summary.py # derived.csv → platform_supply_summary.csv
```

## Data Flow

```
Input/Raw CSVs/          →  output/facts/facts.csv
(9 platform CSVs)           (schema-conformant facts table)
                                    ↓
                         output/views/derived.csv
                         (with parsed timestamps, age, availability flags)
                                    ↓
                         output/views/platform_supply_summary.csv
                         (final analytical output)
```

## Usage

```bash
cd "Dog Market Robust"
python pipeline/run_pipeline.py
```

## Output Files

### `output/facts/facts.csv`
- **32 columns**: `platform` + 31 schema fields from `pets4homes_master_schema.csv`
- **No derivations** - pure field mapping only
- **19,021 rows** across 9 platforms

### `output/views/derived.csv`
- **58 columns**: facts + parsed timestamps (*_ts), numerics (*_num), and availability flags
- Contains all parsing heuristics:
  - `ready_to_leave_parsed_ts`: Parsed ready-to-leave timestamp
  - `ready_to_leave_parse_mode`: How the value was parsed (date, now, in_weeks, dob_plus_8wks, etc.)
  - `days_until_ready`: Days from asof_ts to ready_to_leave
  - `is_ready_now`: True if available immediately (days_until_ready ≤ 0)
  - `is_waiting_list`: True if future availability (days_until_ready > 0)
  - `availability_known`: True if we successfully parsed ready_to_leave

### `output/views/platform_supply_summary.csv`
- Per-platform summary with:
  - Listing counts
  - Availability coverage and breakdown
  - Price and age statistics
  - Confidence notes

## Platform Coverage Summary

| Platform | Listings | Availability Known | Ready Now | Waiting List | Confidence |
|----------|----------|-------------------|-----------|--------------|------------|
| pets4homes | 7,621 | 100% | 67.2% | 32.8% | High |
| freeads | 6,561 | 15.7% | 13.7% | 2.0% | Medium |
| gumtree | 1,775 | 100% | 67.3% | 32.7% | High |
| preloved | 678 | 50% | 49.7% | 0.3% | Low |
| foreverpuppy | 636 | 0% | 0% | 0% | Low |
| petify | 602 | 7% | 5.8% | 1.2% | Low |
| puppies | 575 | 8.9% | 4.5% | 4.3% | Low |
| kennel_club | 411 | 99.8% | 76.9% | 22.9% | Medium |
| champdogs | 162 | 100% | 11.7% | 88.3% | Medium |

**Totals**: 19,021 listings | 41.8% ready now | 18.3% waiting list | 39.9% unknown

## Parsing Heuristics

### Puppy count extraction (in facts, pipeline_01)

| Platform | Raw Field | Parsing Rule | Coverage |
|----------|-----------|--------------|----------|
| pets4homes | `total_available` | Direct mapping | 100% |
| foreverpuppy | `total_available` | Direct mapping | 94.2% |
| petify | `males_available` + `females_available` | Sum when total missing | 100% (via gender) |
| kennel_club | `litter_size` | Parse "X Bitch, Y Dog" → sum | 100% (411 listings) |
| champdogs | `puppies_available` | Direct mapping (currently NULL in scrape) | 0% |
| Other platforms | None | NOT extracted from raw CSVs | 0% |

**Kennel Club Extraction Details** (Jan 22, 2026):
- Added `parse_kennel_club_litter_size()` function to convert "2 Bitch, 3 Dog" → 5
- Applied to 411 Kennel Club listings, extracting 2,453 puppies
- Average 5.97 puppies per litter (min=1, max=12)
- See: [pipeline_01_build_facts.py lines 25-54](pipeline_01_build_facts.py#L25)

### Ready-to-leave parsing (in views, not facts)

| Platform | Approach | Example Values |
|----------|----------|---------------|
| pets4homes | Direct date parsing | `2026-02-15` |
| gumtree | Pattern matching | `Now`, `in 2 weeks` |
| freeads | Mixed: Now, weeks, date anchoring | `Now`, `8 weeks`, `7th February` |
| kennel_club/champdogs | DOB + 8 weeks fallback | Uses `date_of_birth` + 56 days |
| Others | Date parsing where available | Various |

### Freeads date anchoring
For date strings like "7th February":
1. Anchor to `asof_ts` year
2. If result is >180 days in the past, bump to next year
3. If result is >180 days in the future, mark as `date_suspicious`

### DOB + 8 weeks heuristic
For platforms with `date_of_birth` but no `ready_to_leave`:
- Estimate `ready_to_leave_parsed_ts = date_of_birth + 8 weeks`
- Mark parse_mode as `dob_plus_8wks`

## Key Assumptions

1. **Schema conformance**: Facts table strictly matches `pets4homes_master_schema.csv` + `platform`
2. **Puppies ready at 8 weeks**: Standard weaning age used for DOB-based estimation
3. **180-day window**: Date anchoring assumes dates refer to the nearest reasonable year
4. **asof_ts anchor**: Pipeline run timestamp used as reference for relative dates
5. **Kennel Club litter format**: Assumes "X Bitch, Y Dog" format in litter_size field

## Data Quality & Validation

### Puppy count validation (pipeline_02)
- Flags suspicious values: `total_available > 20` or year-like values (1800-2099) or prices > £500
- 22 suspicious entries caught in freeads (data corruption with year/price values parsed as counts)
- Recalculates from gender splits (`males_available + females_available`) when available
- See: [pipeline_02_build_derived.py lines 358-410](pipeline_02_build_derived.py#L358)

### Known data issues
- **Champdogs**: `puppies_available` field exists in raw CSV but is 100% NULL (scraper issue, not extraction issue)
- **Gumtree, Freeads, Preloved, Puppies**: No explicit puppy count in raw CSVs (could be extracted from title/description via pattern matching if needed)

## What's NOT in this pipeline (intentionally)

- No v2/v3 file variants
- No timestamped output files (single authoritative file per stage)
- No intermediate canonical layer (facts reads directly from raw CSVs)
- No cross-platform deduplication (each platform's data preserved as-is)
