#!/usr/bin/env python3
"""
Export dog market data to SQLite database for SQL-based queries
"""

import pandas as pd
import sqlite3
from pathlib import Path

print("Creating SQLite database...\n")

# Load data
facts = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

# Create database
db_path = Path('output/dog_market.db')
conn = sqlite3.connect(db_path)

print(f"Exporting facts table ({len(facts)} rows)...")
facts.to_sql('facts', conn, if_exists='replace', index=False)

print(f"Exporting derived table ({len(derived)} rows)...")
derived.to_sql('derived', conn, if_exists='replace', index=False)

# Create indexes for faster queries
print("\nCreating indexes...")
conn.execute('CREATE INDEX idx_facts_platform ON facts(platform)')
conn.execute('CREATE INDEX idx_facts_breed ON facts(breed)')
conn.execute('CREATE INDEX idx_facts_location ON facts(location)')
conn.execute('CREATE INDEX idx_facts_seller ON facts(seller_name)')
conn.execute('CREATE INDEX idx_derived_platform ON derived(platform)')
conn.execute('CREATE INDEX idx_derived_breed ON derived(breed)')

conn.commit()
conn.close()

print(f"\n✓ Database created: {db_path}")
print(f"  Size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")

# Show how to use it
print("\n" + "=" * 80)
print("HOW TO USE THE DATABASE\n")

print("""
# In Python:
import sqlite3
conn = sqlite3.connect('output/dog_market.db')
df = pd.read_sql_query('SELECT * FROM derived WHERE platform = "gumtree" LIMIT 10', conn)

# Via command line:
sqlite3 output/dog_market.db
sqlite> SELECT COUNT(*), platform FROM facts GROUP BY platform;
sqlite> SELECT breed, AVG(price_num) as avg_price FROM derived GROUP BY breed ORDER BY avg_price DESC LIMIT 10;
sqlite> SELECT location, COUNT(*) as listings FROM facts GROUP BY location ORDER BY listings DESC LIMIT 10;

# Common Queries:
SELECT COUNT(*), platform FROM facts GROUP BY platform;
SELECT DISTINCT breed FROM facts ORDER BY breed;
SELECT location, AVG(price_num) as avg_price, COUNT(*) as listings 
  FROM derived GROUP BY location HAVING listings > 10 ORDER BY listings DESC;
SELECT platform, microchipped, COUNT(*) 
  FROM derived WHERE microchipped IS NOT NULL GROUP BY platform, microchipped;
""")

print("\n" + "=" * 80)
print("TABLE SCHEMAS\n")

print("FACTS table:")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(facts)")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

print("\nDERIVED table:")
cursor.execute("PRAGMA table_info(derived)")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

conn.close()
