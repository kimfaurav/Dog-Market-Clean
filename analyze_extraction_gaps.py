import pandas as pd
from pathlib import Path

raw_dir = Path("Input/Raw CSVs")

# Map of platform -> raw file
raw_files = {
    "pets4homes": "pets4homes_v7_complete copy.csv",
    "gumtree": "gumtree_final copy.csv",
    "freeads": "freeads_enriched_COMPLETE copy.csv",
    "preloved": "preloved_enriched copy.csv",
    "kennel_club": "kc_data_PERFECT copy.csv",
    "foreverpuppy": "foreverpuppy_FINAL copy.csv",
    "petify": "petify_data_clean copy.csv",
    "puppies": "puppies_final copy.csv",
    "champdogs": "champdogs_complete copy.csv",
}

print("ANALYSIS OF EXTRACTION GAPS\n")
print("=" * 80)

for platform, filename in sorted(raw_files.items()):
    path = raw_dir / filename
    if path.exists():
        raw_df = pd.read_csv(path, nrows=0)
        raw_cols = set(raw_df.columns.tolist())
        
        # Load facts to see what was extracted
        facts = pd.read_csv('output/facts/facts.csv', nrows=0)
        facts_cols = set(facts.columns.tolist())
        
        # Platforms have a 'platform' column added, so exclude that
        platform_specific = facts_cols - {'platform'}
        
        # What was available but not used?
        # (We look at just this platform's potential fields)
        unmapped = raw_cols - platform_specific
        
        print(f"\n{platform.upper()}")
        print(f"  Raw CSV: {len(raw_cols)} fields")
        print(f"  Extracted to facts: {len(raw_df.columns.tolist()) if platform != 'pets4homes' else len([c for c in raw_cols if c in platform_specific])} fields")
        print(f"  Available fields not in master schema: {len(unmapped)}")
        if unmapped:
            print(f"  → {', '.join(sorted(unmapped)[:8])}")
            if len(unmapped) > 8:
                print(f"    ... and {len(unmapped) - 8} more")

print("\n" + "=" * 80)
print("\nKEY QUESTION: Are these unmapped fields valuable?")
