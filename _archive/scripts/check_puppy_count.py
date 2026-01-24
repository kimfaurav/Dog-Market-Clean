import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', dtype=str, keep_default_na=False)
facts['total_available_num'] = pd.to_numeric(facts['total_available'], errors='coerce')

print("=" * 70)
print("PUPPY COUNT BY PLATFORM - UPDATED WITH KENNEL CLUB EXTRACTION")
print("=" * 70)

for platform in sorted(facts['platform'].unique()):
    pf = facts[facts['platform'] == platform]
    count = pf['total_available_num'].notna().sum()
    total = pf['total_available_num'].sum()
    avg = pf['total_available_num'].mean() if count > 0 else 0
    pct = 100*count/len(pf) if len(pf) > 0 else 0
    print(f"{platform:15} {len(pf):5} listings | {int(total):7} puppies | {avg:5.2f} avg | {int(count):4} with data ({pct:5.1f}%)")

print()
total_listings = facts['total_available_num'].notna().sum()
total_puppies = facts['total_available_num'].sum()
print(f"TOTAL: {int(total_puppies):7} puppies from {int(total_listings):5} listings")
