# Platform-Specific Notes

## Overview

Each platform has different data quality, what they track, and how they structure information.

---

## PETS4HOMES (40.1% of data - 7,621 listings)

**Strengths:**
- Best structured data
- Consistent fields across listings
- Seller reputation tracked (reviews, ratings)
- Account age and activity tracking
- License information sometimes included
- Detailed availability info

**Weaknesses:**
- Some sellers use misleading names/info
- Limited health data in structured fields
- Price can vary significantly

**Key Fields:**
- `user_type`: Always populated (Breeder, Professional, Private)
- `reviews` & `rating`: Good for seller reputation
- `is_breeder`: Marked by platform
- `license_num`: Some sellers include license

**Quirks:**
- Seller "last_active" timestamp is reliable (shows active sellers)
- "active_listings" and "active_pets" show seller scale
- Price marked up if marked as "Licensed Breeder"

**Data Quality:** ★★★★★ Excellent

---

## FREEADS (34.5% of data - 6,561 listings)

**Strengths:**
- Large volume of listings
- Good health data when provided (microchipped, vaccinated, wormed, etc.)
- Quality indicators (pedigree, champion bloodline, dna_tested)
- Some delivery options tracked
- Puppy contracts and insurance fields

**Weaknesses:**
- Inconsistent formatting
- Many listings missing seller names (appears blank)
- Descriptions mixed with title
- Date format inconsistent
- Price sometimes in raw text only

**Key Fields:**
- `health_checked`, `vet_checked`, `wormed`, `flea_treated`: Often populated
- `pedigree`, `dna_tested`, `champion_bloodline`: Quality indicators
- `home_reared`, `family_reared`: Rearing environment
- `delivery_available`: Rare but useful

**Quirks:**
- Ready date field is "ready_date" instead of "ready_to_leave"
- Many "Mixed Breed X Crossbreed" combinations
- Location is often just region, not specific address
- Listing title may contain multiple dogs

**Data Quality:** ★★★★☆ Good (with caveats)

**Warning:** Some rescues post on Freeads - check for "Mixed Breed" concentration

---

## GUMTREE (9.3% of data - 1,775 listings)

**Strengths:**
- Clean, structured data
- Good sex/gender information
- Health data often included (microchipped, vaccinated, health_checked)
- Ready availability ("Now" vs "in X weeks") is reliable
- Age detail field

**Weaknesses:**
- Short listings, limited detail
- No seller reputation/reviews
- Price sometimes rounded
- Minimal breeding lineage info

**Key Fields:**
- `sex`: Almost always populated
- `microchipped`, `vaccinated`: Good coverage
- `health_checked`: Often populated
- `ready_to_leave`: "Now" or "in 3 weeks" pattern - very reliable

**Quirks:**
- Ready date is parsed as "now" or "in_weeks" - highly reliable (100% success rate)
- Age_detail sometimes just "8 weeks", sometimes with DOB
- No seller reviews or ratings
- Descriptions are short

**Data Quality:** ★★★★☆ Good (structured but minimal)

**Note:** Gumtree data is very clean for ready_to_leave parsing

---

## KENNEL CLUB (2.2% of data - 411 listings)

**Strengths:**
- High-quality, registered breeders only
- Pedigree information tracked (sire, dam)
- Sex/color information
- Breeding specialization (single breed focus)
- License information

**Weaknesses:**
- Small volume
- Price sometimes missing
- Limited availability info
- No seller reputation metrics

**Key Fields:**
- `sire`, `dam`: Usually populated (lineage tracking)
- `sex`, `colour`: Always populated
- `breed`: Highly specialized (usually one breed per breeder)
- `license_number`, `council`: Registration authority

**Quirks:**
- All sellers are registered with Kennel Club
- Price may be by request ("POA")
- Ready date often just "date_born" without actual availability
- No seller reviews (reputation based on KC registration)

**Data Quality:** ★★★★★ Excellent (but limited scope)

**Note:** Best source for pedigree and breeding information

---

## PRELOVED (3.6% of data - 678 listings)

**Strengths:**
- Good health info when present
- Seller reputation visible (member_since, views)
- Moderate volume
- Seller type tracked

**Weaknesses:**
- About 50% missing ready_to_leave date
- Limited sex/color information
- Some blank seller names
- Inconsistent formatting

**Key Fields:**
- `seller_type`: Often populated (Private, Professional, etc.)
- `member_since`: Account age indicator
- `views`: Popular listing indicator
- Health fields when populated

**Quirks:**
- Many rescue listings mixed with breeders
- Ready_to_leave often missing (need to use DOB + 8 weeks)
- Location sometimes just postcode

**Data Quality:** ★★★☆☆ Fair (spotty coverage)

---

## FOREVERPUPPY (3.3% of data - 636 listings)

**Strengths:**
- Seller type tracked (PRIVATE, COMMERCIAL, RESCUE)
- Gender counts (boys/girls)
- Some health info

**Weaknesses:**
- ~50% missing ready_to_leave date
- Many blank seller names
- Limited health fields
- Descriptions inconsistent

**Key Fields:**
- `boys`, `girls`: Gender-specific counts
- `seller_type`: Classification
- `available`: Boolean flag

**Quirks:**
- Data quality varies significantly
- Some listings reposted frequently
- Limited seller reputation info
- Location inconsistently formatted

**Data Quality:** ★★★☆☆ Fair

---

## PETIFY (3.2% of data - 602 listings)

**Strengths:**
- ID verification tracked
- Seller type available
- Some health data
- Price consistency good

**Weaknesses:**
- Low volume
- Limited ready_to_leave data
- Minimal breeding info
- Some listings missing seller info

**Key Fields:**
- `id_verified`: Seller verification flag
- `seller_type`: Classification
- `microchipped`, `vaccinated`: When available

**Quirks:**
- Newer platform, lower volume
- Limited coverage for specialized fields
- Focus on general seller categories

**Data Quality:** ★★★☆☆ Fair

---

## PUPPIES.CO.UK (3.0% of data - 575 listings)

**Strengths:**
- Health info tracked (health_tested, vet_checked)
- Breeder-focused
- Litter info (how many in litter)
- Some pedigree info

**Weaknesses:**
- Moderate volume
- Limited sex/color info
- Some missing availability dates
- No seller reviews/ratings

**Key Fields:**
- `health_tested`, `vet_checked`: Often populated
- `sire_info`, `dam_info`: Parent information
- `seller_type`: Classification

**Quirks:**
- Descriptions can be verbose
- Litter size tracked
- Some missing ad_reference
- Good for breeding analysis

**Data Quality:** ★★★★☆ Good (breeding-focused)

---

## CHAMPDOGS (0.9% of data - 162 listings)

**Strengths:**
- Premium breeders only
- Full lineage info (sire, dam names)
- Breeder credibility tracked (five_star, assured, licensed)
- Health info included
- Highest quality breeding info

**Weaknesses:**
- Smallest volume (only 162 listings)
- Limited to professional breeders
- Some price by request
- Expensive puppies (skews pricing analysis)

**Key Fields:**
- `sire_name`, `dam_name`: Full lineage
- `five_star_breeder`, `assured_breeder`, `licensed_breeder`: Credibility indicators
- `health_tested`, `health_checks`: Health info
- `breeder_url`: Direct contact

**Quirks:**
- All premium/certified breeders
- Price often higher
- Descriptions detailed
- Litter planning evident

**Data Quality:** ★★★★★ Excellent (premium subset)

**Note:** Best for premium breeder analysis, but not representative of overall market

---

## Summary Table

| Platform | Volume | Data Quality | Best For | Caveats |
|----------|--------|--------------|----------|---------|
| Pets4Homes | 40% | ★★★★★ | Market overview, seller reputation | Large, general market |
| Freeads | 35% | ★★★★☆ | Health data, quality indicators | Rescues mixed in |
| Gumtree | 9% | ★★★★☆ | Ready availability, structured data | Minimal detail |
| Kennel Club | 2% | ★★★★★ | Pedigree, premium breeders | Small, filtered market |
| Preloved | 4% | ★★★☆☆ | Seller comparison | Spotty coverage |
| Foreverpuppy | 3% | ★★★☆☆ | Gender counts | Limited fields |
| Petify | 3% | ★★★☆☆ | ID verification | Low volume |
| Puppies | 3% | ★★★★☆ | Breeding analysis | Moderate volume |
| Champdogs | 1% | ★★★★★ | Premium market | Premium subset only |

---

## Recommendations

### For Market Overview
Use **Pets4Homes + Freeads** (75% of data, good coverage)

### For Breeding Analysis
Use **Kennel Club + Champdogs + Puppies** (premium/serious breeders)

### For Price Analysis
Use **All except Champdogs** (Champdogs skews high)

### For Health Data
Use **Freeads + Gumtree + Pets4Homes** (best coverage)

### For Availability Trends
Use **Gumtree** (100% parse success rate on ready_to_leave)

### For Seller Reputation
Use **Pets4Homes** (only platform with reviews)
