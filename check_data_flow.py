import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

print("CHAMPDOGS DATA FLOW:")
print("="*80)

champdogs_facts = facts[facts['platform'] == 'champdogs']
champdogs_derived = derived[derived['platform'] == 'champdogs']

print(f"\nFacts: {len(champdogs_facts)} rows")
print(f"  total_available value counts:")
print(champdogs_facts['total_available'].value_counts(dropna=False).head(15))

print(f"\nDerived: {len(champdogs_derived)} rows")
print(f"  total_available_num value counts:")
print(champdogs_derived['total_available_num'].value_counts(dropna=False).head(15))
print(f"  total_available_flag:")
print(champdogs_derived['total_available_flag'].value_counts(dropna=False))

print("\n" + "="*80)
print("KENNEL CLUB DATA FLOW:")
print("="*80)

kc_facts = facts[facts['platform'] == 'kennel_club']
kc_derived = derived[derived['platform'] == 'kennel_club']

print(f"\nFacts: {len(kc_facts)} rows")
print(f"  total_available value counts:")
print(kc_facts['total_available'].value_counts(dropna=False).head(15))

print(f"\nDerived: {len(kc_derived)} rows")
print(f"  total_available_num value counts:")
print(kc_derived['total_available_num'].value_counts(dropna=False).head(15))
print(f"  total_available_flag:")
print(kc_derived['total_available_flag'].value_counts(dropna=False))
