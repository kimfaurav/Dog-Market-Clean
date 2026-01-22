import pandas as pd
from pathlib import Path

raw_dir = Path("Input/Raw CSVs")

# Check what fields are available in each platform
platforms = {
    'gumtree': 'gumtree_final*.csv',
    'preloved': 'preloved_enriched*.csv',
    'champdogs': 'champdogs_complete*.csv',
    'freeads': 'freeads_enriched_COMPLETE*.csv',
    'puppies': 'puppies_final*.csv',
}

for platform, pattern in platforms.items():
    files = list(raw_dir.glob(pattern))
    if files:
        file_path = sorted(files)[-1]
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False, low_memory=False)
        print(f"\n{platform.upper()}: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
