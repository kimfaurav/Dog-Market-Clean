# Data Dictionary - Dog Market Dataset

## Core Identity Fields

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `url` | string | Listing URL | 100% | Unique identifier for listing |
| `ad_id` | string | Platform-specific ad ID | 54.2% | Useful for tracking over time |
| `platform` | string | Source platform | 100% | One of 9 platforms |
| `seller_name` | string | Seller/breeder name | 95.1% | May be blank on some platforms |
| `seller_id` | string | Platform seller ID | 28.3% | Not consistently available |

## Dog Attributes

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `breed` | string | Dog breed | 100% | Standardized names from scrapes |
| `sex` | string | M/F or mixed | 35.8% | Often missing from listings |
| `color` | string | Coat color | 21.2% | Only from specialty platforms |
| `date_of_birth` | string | Puppy DOB | 43.3% | Raw format, see `age_days` for parsed |
| `age_days` | numeric | Age in days | 43.3% | Calculated from DOB or ready_to_leave |
| `title` | string | Listing title | 95.9% | Raw listing text |

## Price & Availability

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `price` | string | Listed price (raw) | 96.9% | Currency symbol varies |
| `price_num` | numeric | Price parsed to number | 96.9% | Use this for analysis |
| `males_available` | string | Male puppies count | 47.5% | Often missing |
| `females_available` | string | Female puppies count | 47.5% | Often missing |
| `total_available` | string | Total puppies count | 47.5% | Use `total_available_num` for analysis |
| `total_available_num` | numeric | Parsed total available | 47.5% | Capped at 16 (realistic max) |

## Dates & Timeline

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `published_at` | string | Listing publish date | 91.1% | First posted date |
| `published_at_ts` | datetime | Parsed publish timestamp | 91.1% | Use for date comparisons |
| `created_at` | string | Account/listing creation | 40.1% | Not all platforms track |
| `refreshed_at` | string | Last refresh date | 40.1% | Shows if listing was bumped |
| `ready_to_leave` | string | Availability date (raw) | 63.2% | Format varies wildly |
| `ready_to_leave_parsed_ts` | datetime | Availability parsed | 40.2% | Only when successfully parsed |
| `ready_to_leave_parse_mode` | string | How availability was determined | 100% | See Parse Modes section |

## Health & Medical

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `microchipped` | boolean/string | Microchip status | 32.3% | Y/N or true/false format |
| `vaccinated` | boolean/string | Vaccination status | 29.5% | Y/N or true/false format |
| `health_checked` | boolean/string | Health screening done | 16.5% | Y/N or true/false format |
| `health_tested` | boolean/string | Genetic health testing | 1.2% | Rare, mostly from specialist platforms |
| `vet_checked` | boolean/string | Professional vet check | 5.1% | Y/N or true/false format |
| `wormed` | boolean/string | Deworming done | 23.3% | Y/N or true/false format |
| `flea_treated` | boolean/string | Flea treatment done | 12.1% | Y/N or true/false format |

## Breeding & Lineage

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `sire` | string | Father dog name/info | 3.9% | Usually just name, from specialty platforms |
| `dam` | string | Mother dog name/info | 4.6% | Usually just name, from specialty platforms |
| `sire_health_tested` | boolean/string | Sire health screening | 0.3% | Rare, breeding-focused platforms |
| `dam_health_tested` | boolean/string | Dam health screening | 0.2% | Rare, breeding-focused platforms |
| `pedigree` | boolean/string | Has pedigree documentation | 4.0% | Y/N indicator |
| `dna_tested` | boolean/string | DNA testing done | 1.3% | Genetic screening indicator |
| `champion_bloodline` | boolean/string | From show/championship line | 1.2% | Quality indicator |

## Seller/Breeder Info

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `company_name` | string | Kennel/business name | 20.2% | Registered business name |
| `user_type` | string | Seller classification | 51.6% | 'Breeder', 'Private', 'Professional', etc. |
| `is_breeder` | boolean | Marked as breeder | 40.1% | Platform-specific flag |
| `breeder_verified` | boolean/string | Breeder identity verified | 2.5% | Usually ID verification |
| `license_num` | string | Breeding/business license | 2.3% | Registration number |
| `license_auth` | string | Licensing authority | 2.3% | Council/body issuing license |
| `license_status` | string | License validity | 0.1% | Valid/Expired/Pending |
| `kc_license` | boolean/string | Kennel Club registered | 24% | Prestigious UK registration |
| `member_since` | datetime | Account creation date | 47.1% | Seller history |
| `last_active` | datetime | Last platform activity | 40.1% | Freshness indicator |
| `response_hours` | numeric | Avg response time | 1.4% | Only Pets4Homes |
| `reviews` | numeric | Number of reviews | 20.1% | Reputation metric |
| `rating` | numeric | Average rating (1-5) | 20.1% | Star rating or similar |

## Location & Logistics

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `location` | string | Free-text location | 97.1% | City, region, or postcode area |
| `delivery_available` | boolean/string | Shipping option | 0.6% | Rare, mostly Freeads |
| `puppy_contract` | boolean/string | Contract provided | 0.2% | Legal protection |
| `insurance_available` | boolean/string | Health insurance option | 1.4% | Seller benefit |
| `home_reared` | boolean/string | Raised in home | 1.4% | Quality indicator |
| `family_reared` | boolean/string | Raised with family | 6.5% | Socialization indicator |

## Engagement & Views

| Field | Type | Description | Coverage | Notes |
|-------|------|-------------|----------|-------|
| `views_count` | numeric | Listing views | 20.1% | Popular listing indicator |
| `active_listings` | numeric | Seller active listings | 40.1% | Scale of operation |
| `active_pets` | numeric | Seller total pets | 40.1% | Diversity of breeding |

---

## Derived Fields (in derived.csv only)

| Field | Type | Description | 
|-------|------|-------------|
| `price_num` | numeric | Price as number (no currency) |
| `males_available_num` | numeric | Males available as number |
| `females_available_num` | numeric | Females available as number |
| `total_available_num` | numeric | Total available as number (capped at 16) |
| `age_days` | numeric | Age calculated from DOB |
| `ready_to_leave_parse_mode` | string | Method used to determine availability |
| `ready_to_leave_parsed_ts` | datetime | Absolute timestamp of ready date |
| `pct_ready_now` | float | % of listings ready now |
| `pct_waiting_list` | float | % on waiting list |
| `pct_unknown` | float | % unknown availability |
| `pct_availability_known` | float | % with known availability |

---

## Parse Modes Explained

The `ready_to_leave_parse_mode` field shows HOW the availability date was determined:

| Mode | What It Means | Reliability |
|------|---------------|-------------|
| `date` | Explicit date found in listing | ★★★★★ High |
| `now` | Listing says "available now" | ★★★★★ High |
| `in_weeks` | "In X weeks" pattern parsed | ★★★★★ High |
| `dob_plus_8wks` | Calculated from DOB + 8 weeks | ★★★★☆ Medium-High |
| `date_anchored` | Fuzzy date matched to listing date | ★★★☆☆ Medium |
| `unknown` | Pattern not recognized | ★☆☆☆☆ Low |
| `missing` | No ready date data | ☆☆☆☆☆ None |
| `date_suspicious` | Date seems incorrect | ☆☆☆☆☆ Unreliable |

---

## Data Quality Notes

### High Confidence Fields
- `url`, `breed`, `price_num`, `location`, `platform` - 96-100% complete
- All have been manually verified

### Medium Confidence Fields
- `published_at`, `seller_name`, `title` - 91-95% complete
- Some platforms don't track all fields

### Low Confidence Fields
- Health fields (5-32% coverage) - only populated where platform provides
- Availability counts (47.5%) - many platforms don't separate M/F
- Age data (43%) - calculated from DOB which isn't always provided
- Breeding info (0.2-4%) - only specialist platforms track

### How to Handle Missing Data

```python
# For numerical columns
df['price_num'].fillna(df['price_num'].median())  # Impute with median

# For categorical  
df['microchipped'].fillna('unknown')  # Mark as unknown

# For analysis
df_complete = df.dropna(subset=['price_num', 'location'])  # Drop rows
df_subset = df[df['health_checked'].notna()]  # Filter to complete
```

---

## Field Aliases

Some fields may be referenced by different names:

- `published_at` = `created` (on some platforms)
- `seller_name` = `breeder_name` (in raw data)
- `location` = `county` (in raw data)
- `total_available` = `litter_size` (in raw data)
