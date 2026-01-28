# Scraper Inventory

Complete inventory of all platform scrapers recovered and installed in the project.

## Recovery Summary

| Platform | URL Collector | Enrichment | Source Location | Status |
|----------|---------------|------------|-----------------|--------|
| Pets4Homes | - | `pets4homes_scraper.py` | `~/Desktop/Pets/P4H/pets4homes_scraper_v7.py` | ✅ Recovered |
| FreeAds | `freeads_url_collector.py` | `freeads_scraper.py` | `~/Desktop/Pets/Freeads/` | ✅ Recovered |
| Gumtree | `gumtree_url_collector.py` | `gumtree_scraper.py` | `~/Desktop/Pets/Gumtree/` | ✅ Recovered |
| Preloved | - | `preloved_scraper.py` | `~/Desktop/Pets/Preloved/preloved_PRODUCTION.py` | ✅ Recovered |
| Kennel Club | `kennel_club_url_collector.py` | `kennel_club_scraper.py` | `~/Desktop/Pets/freeads-breeds/` | ✅ Recovered |
| Champdogs | - | `champdogs_scraper.py` | `~/Desktop/Pets/Champdogs/champdogs_scraper_PRODUCTION.py` | ✅ Recovered |
| ForeverPuppy | - | `foreverpuppy_scraper.py` | `~/Desktop/Pets/ForeverPuppy/foreverpuppy_ALL.py` | ✅ Recovered |
| Puppies | - | `puppies_scraper.py` | `~/Desktop/Pets/puppies_golden_scraper.py` | ✅ Recovered |
| Petify | - | `petify_scraper.py` | Already in project | ✅ Present |
| Gundogs Direct | - | `gundogs_direct_scraper.py` | Already in project | ✅ Present |

**All 10 platforms now have scrapers.**

---

## Scraper Details

### 1. Pets4Homes

| Property | Value |
|----------|-------|
| File | `scrapers/pets4homes_scraper.py` |
| Framework | requests + BeautifulSoup |
| Type | Combined (URL discovery + enrichment) |
| Headless | Yes (no browser needed) |

**Usage:**
```bash
python scrapers/pets4homes_scraper.py
```

**Notes:**
- Iterates through 200+ breed URLs
- Extracts from listing pages and detail pages
- Largest dataset (~97k rows)

---

### 2. FreeAds

| Property | Value |
|----------|-------|
| URL Collector | `scrapers/freeads_url_collector.py` |
| Enrichment | `scrapers/freeads_scraper.py` |
| Framework | requests (collector), Playwright async (enrichment) |
| Headless | Yes |

**Usage:**
```bash
# Phase 1: Collect URLs
python scrapers/freeads_url_collector.py

# Phase 2: Enrich
python scrapers/freeads_scraper.py
```

**Notes:**
- Two-phase process
- 35 fields extracted
- Async Playwright for speed

---

### 3. Gumtree

| Property | Value |
|----------|-------|
| URL Collector | `scrapers/gumtree_url_collector.py` |
| Enrichment | `scrapers/gumtree_scraper.py` |
| Framework | Playwright (sync) |
| Headless | No (`headless=False` required) |

**Usage:**
```bash
cd scrapers

# Phase 1: Collect URLs (30-60 min)
python gumtree_url_collector.py
# → gumtree_ULTIMATE_urls.txt

# Phase 2: Enrich (1-2 hours)
python gumtree_scraper.py gumtree_ULTIMATE_urls.txt output.json
```

**Notes:**
- Requires visible browser (Cloudflare protection)
- SVG color detection for health badges
- 163 breed slugs

---

### 4. Preloved

| Property | Value |
|----------|-------|
| File | `scrapers/preloved_scraper.py` |
| Framework | Selenium |
| Type | Combined (search + enrichment) |
| Headless | Configurable |

**Usage:**
```bash
python scrapers/preloved_scraper.py
```

**Notes:**
- Uses Selenium (not Playwright)
- Searches multiple keywords
- 280+ breed patterns
- Extensive filter list for non-dog items

---

### 5. Kennel Club

| Property | Value |
|----------|-------|
| URL Collector | `scrapers/kennel_club_url_collector.py` |
| Enrichment | `scrapers/kennel_club_scraper.py` |
| Framework | Selenium |
| Headless | No (visible browser) |

**Usage:**
```bash
# Phase 1: Collect from search
python scrapers/kennel_club_url_collector.py

# Phase 2: Enrich each listing
python scrapers/kennel_club_scraper.py
```

**Notes:**
- License tracking available
- Requires navigation through search results
- Health testing data from detail pages

---

### 6. Champdogs

| Property | Value |
|----------|-------|
| File | `scrapers/champdogs_scraper.py` |
| Framework | Playwright (sync) |
| Type | Combined |
| Headless | Yes |

**Usage:**
```bash
python scrapers/champdogs_scraper.py
```

**Notes:**
- Detail pages require login (scrapes from cards only)
- Extracts: breed, sire, dam, location, born date, health tested
- Litters, not individual puppies

---

### 7. ForeverPuppy

| Property | Value |
|----------|-------|
| File | `scrapers/foreverpuppy_scraper.py` |
| Framework | Playwright (async) |
| Type | Combined |
| Headless | Yes |

**Usage:**
```bash
python scrapers/foreverpuppy_scraper.py
```

**Notes:**
- Scrapes all ad types: for-sale, for-stud, wanted, rehome
- Paginates through all results
- Async for performance

---

### 8. Puppies.co.uk

| Property | Value |
|----------|-------|
| File | `scrapers/puppies_scraper.py` |
| Framework | Playwright (sync) |
| Type | Combined |
| Headless | No (`headless=False`) |

**Usage:**
```bash
python scrapers/puppies_scraper.py
python scrapers/puppies_scraper.py --resume  # Resume from checkpoint
```

**Notes:**
- Supports resume from checkpoint
- 25 fields extracted
- Visible browser required

---

### 9. Petify

| Property | Value |
|----------|-------|
| File | `scrapers/petify_scraper.py` |
| Framework | Playwright (sync) |
| Type | Combined |
| Headless | Yes |

**Usage:**
```bash
python scrapers/petify_scraper.py
```

**Notes:**
- Already present in project
- Seller names are initials only

---

### 10. Gundogs Direct

| Property | Value |
|----------|-------|
| File | `scrapers/gundogs_direct_scraper.py` |
| Framework | Playwright (sync) |
| Type | Combined |
| Headless | Yes |

**Usage:**
```bash
python scrapers/gundogs_direct_scraper.py
```

**Notes:**
- Already present in project
- Specialized for gundog breeds

---

## Dependencies by Framework

### Playwright (8 scrapers)
```bash
pip install playwright
playwright install chromium
```

Used by: Gumtree, FreeAds (enrichment), Champdogs, ForeverPuppy, Puppies, Petify, Gundogs Direct

### Selenium (2 scrapers)
```bash
pip install selenium webdriver-manager
```

Used by: Preloved, Kennel Club

### Requests + BeautifulSoup (2 scrapers)
```bash
pip install requests beautifulsoup4
```

Used by: Pets4Homes, FreeAds (URL collector)

---

## Platform-Specific Notes

### Rate Limiting
| Platform | Delay | Notes |
|----------|-------|-------|
| Pets4Homes | 2-5s | Standard rate limit |
| FreeAds | 1.5-3s | Async handles multiple |
| Gumtree | 2-4s | Cloudflare protected |
| Preloved | Random | Varies by search |
| Kennel Club | 5s | Conservative |
| Champdogs | 1.5-3.5s | Standard |
| ForeverPuppy | 1-2s | Fast async |
| Puppies | 2-4s | Standard |
| Petify | 1-2s | Standard |
| Gundogs Direct | 1-2s | Standard |

### Browser Requirements
| Requirement | Platforms |
|-------------|-----------|
| Visible browser required | Gumtree, Puppies, Kennel Club |
| Headless OK | All others |

### Authentication
| Requirement | Platforms |
|-------------|-----------|
| Login required for detail | Champdogs |
| No auth needed | All others |

---

## Verification Checklist

```
✅ Pets4Homes    - scrapers/pets4homes_scraper.py
✅ FreeAds       - scrapers/freeads_url_collector.py + freeads_scraper.py
✅ Gumtree       - scrapers/gumtree_url_collector.py + gumtree_scraper.py
✅ Preloved      - scrapers/preloved_scraper.py
✅ Kennel Club   - scrapers/kennel_club_url_collector.py + kennel_club_scraper.py
✅ Champdogs     - scrapers/champdogs_scraper.py
✅ ForeverPuppy  - scrapers/foreverpuppy_scraper.py
✅ Puppies       - scrapers/puppies_scraper.py
✅ Petify        - scrapers/petify_scraper.py
✅ Gundogs Direct - scrapers/gundogs_direct_scraper.py
```

**Total: 10/10 platforms covered**

---

*Inventory completed: January 2026*
