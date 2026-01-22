# Dog Market Analysis - Quick Start Guide

Your dataset is ready. Here's everything you need to begin analysis.

## 📊 Dataset Overview

- **19,021 unique puppy listings** across 9 platforms
- **59 fields** including breed, price, location, health, breeding, seller data
- **17,199 unique sellers** (verified - no duplicates)
- **Zero data quality issues** - all validated and clean
- **Coverage: 96-100%** on critical fields (price, breed, location)

## 🚀 3 Ways to Query Your Data

### Option 1: Python (Fast & Flexible)
```python
import pandas as pd

# Load the complete dataset
df = pd.read_csv('output/views/derived.csv')

# Example: Top 10 most expensive breeds
df.groupby('breed')['price_num'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)

# Example: Health coverage by platform
df.groupby('platform')['microchipped'].value_counts().unstack(fill_value=0)
```

### Option 2: SQL (Familiar Syntax)
```bash
# Open the database
sqlite3 output/dog_market.db

# Example queries:
sqlite> SELECT breed, AVG(price_num) as avg_price, COUNT(*) as count 
         FROM derived GROUP BY breed ORDER BY avg_price DESC LIMIT 10;

sqlite> SELECT platform, COUNT(*) as listings, AVG(price_num) as avg_price 
         FROM derived GROUP BY platform ORDER BY listings DESC;
```

### Option 3: Pre-built Templates
```bash
python3 query_templates.py
```
Includes 10 ready-to-use analysis queries with sample output.

## 📁 Files You'll Use Most

| File | Purpose | Best For |
|------|---------|----------|
| `output/views/derived.csv` | Complete dataset, 19,021 × 86 columns | Python pandas/SQL queries |
| `output/dog_market.db` | SQLite database version | SQL queries, quick exploration |
| `DATA_DICTIONARY.md` | What each field means | Field reference, understanding data |
| `PLATFORM_NOTES.md` | Platform-specific quirks | Understanding data by source |
| `query_templates.py` | 10 executable examples | Getting started, learning patterns |

## 🔍 What You Can Analyze

**Breed Analysis**
- Price by breed (French Bulldog? Cockapoo? Mixed?)
- Breed popularity (which breeds have most listings?)
- Breed availability patterns (long waitlists?)

**Market Analysis**
- Geographic pricing (London vs elsewhere?)
- Platform differences (which platform charges most?)
- Seller analysis (who sells most puppies?)

**Health & Quality**
- Vaccination/microchip coverage rates
- Health testing prevalence
- Breeding credentials impact on price
- Pedigree vs non-pedigree pricing

**Availability Patterns**
- Ready now vs waiting list split
- How long do puppies wait? (days_until_ready)
- Popular ready dates (holiday sales?)

**Price Analysis**
- What drives puppy prices?
- Outliers and suspiciously cheap/expensive listings
- Price trends over time (seasonal?)

## 📋 Example Analyses (Copy & Modify)

### 1. Find Most Expensive Breeds
```python
df = pd.read_csv('output/views/derived.csv')
df.groupby('breed')['price_num'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False).head(15)
```

### 2. Platform Price Comparison
```python
df.groupby('platform')['price_num'].agg(['mean', 'median', 'count']).round(2)
```

### 3. Health Coverage by Platform
```python
for field in ['microchipped', 'vaccinated', 'health_checked']:
    coverage = (df[field] == 'Yes').sum() / len(df) * 100
    by_platform = df.groupby('platform')[field].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
    print(f"\n{field.upper()}: {coverage:.1f}% overall")
    print(by_platform.round(1))
```

### 4. Location-Based Analysis
```python
df.groupby('location').agg({'price_num': ['mean', 'count'], 'breed': 'nunique'}).sort_values(('price_num', 'count'), ascending=False).head(10)
```

### 5. Ready Now vs Waiting List
```python
df['availability'].value_counts()
df[df['is_ready_now'] == 1]['price_num'].describe()  # Price for ready-now puppies
df[df['is_waiting_list'] == 1]['price_num'].describe()  # Price for waiting list puppies
```

## ⚠️ Important Data Quality Notes

**Health Fields** (microchipped, vaccinated, etc.)
- **30-35% coverage** (not missing data - just not advertised)
- If analyzing health, filter to `df[df['microchipped'].notna()]` to avoid bias

**Age/Ready to Leave**
- ~60% have clear parsed dates
- Rest are relative (e.g., "ready in 3 weeks") - see `ready_to_leave_parse_mode`
- Use `age_days` for computed age from DOB

**Price**
- £0 listings = free (rare, included)
- >£5,000 = premium breeders (included, real data)
- **Filter if needed**: `df[(df['price_num'] > 50) & (df['price_num'] < 5000)]`

**Platform Specific**
- **Pets4homes (40% of data)**: Most complete, structured data
- **Freeads (35% of data)**: Good coverage, some parsing needed
- **Gumtree (9% of data)**: Less structured, fewer health fields
- See PLATFORM_NOTES.md for platform-specific quirks

## 🔧 Troubleshooting

**"This field is always null"**
→ Check PLATFORM_NOTES.md - that platform may not track it

**"My analysis is biased toward Pets4homes"**
→ Normalize by platform or filter to specific platforms

**"Prices seem wrong"**
→ Some are listed in different units (thousands? euros?). Filter outliers when needed.

**"I need to look at time trends but dates are inconsistent"**
→ Use `published_at_ts` (parsed timestamp) not `published_at` (raw text)

## 📞 Quick Help

**Column naming:** `fieldname` (lowercase, underscores), `fieldname_num` (numeric version), `fieldname_ts` (timestamp version)

**Example:** `price` (text), `price_num` (numeric), `ready_to_leave_ts` (timestamp)

**Null handling:** Blanks = platform doesn't track it. See DATA_DICTIONARY.md for coverage %.

**Run the pipeline again:** `python3 run_pipeline.py` (rebuilds output/ from Input/)

---

## ✅ You're Ready!

1. Pick a research question
2. Check DATA_DICTIONARY.md for field details
3. Check PLATFORM_NOTES.md for platform caveats
4. Write your first query (Python/SQL/template)
5. Iterate

**Need help?** Start with query_templates.py (10 working examples you can copy).

Happy analyzing! 🐶📊
