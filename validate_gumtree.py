import pandas as pd
import re

df = pd.read_csv('output/views/derived.csv', low_memory=False)
df_unique = df.drop_duplicates(subset=['breed', 'location', 'price_num'], keep='first')

gumtree = df_unique[df_unique['platform'] == 'gumtree'].copy()

print("GUMTREE VALIDATION: Checking 'available' pattern extraction\n")
print("="*80)

# Extract what we found
available_pattern = []
for idx, row in gumtree.iterrows():
    if pd.notna(row['title']):
        title = str(row['title']).lower()
        match = re.search(r'(\d+)\s+(?:available|ready)', title)
        if match:
            available_pattern.append({
                'breed': row['breed'],
                'location': row['location'],
                'price_num': row['price_num'],
                'title': row['title'],
                'extracted_count': int(match.group(1)),
                'total_available_num': row['total_available_num'],
                'males_available_num': row['males_available_num'],
                'females_available_num': row['females_available_num']
            })

if available_pattern:
    avail_df = pd.DataFrame(available_pattern)
    print(f"Found {len(avail_df)} listings matching 'X available/ready' pattern\n")
    
    # Analyze the numbers
    print("Distribution of extracted counts:")
    print(avail_df['extracted_count'].describe())
    
    print(f"\nTop 20 extracted counts:")
    print(avail_df.nlargest(20, 'extracted_count')[['breed', 'location', 'price_num', 'extracted_count', 'title']].to_string())
    
    print(f"\n\nDetailed review of top extractions (to validate):")
    for idx, row in avail_df.nlargest(10, 'extracted_count').iterrows():
        print(f"\n---")
        print(f"Count extracted: {row['extracted_count']}")
        print(f"Title: {row['title']}")
        print(f"Breed: {row['breed']} | Location: {row['location']} | Price: £{row['price_num']:.0f}")
        print(f"Explicit total_available: {row['total_available_num']}")
        print(f"Males: {row['males_available_num']}, Females: {row['females_available_num']}")
else:
    print("No matches found for 'X available/ready' pattern")

print("\n" + "="*80)
print("\nSUMMARY:")
if available_pattern:
    print(f"Pattern extractions: {len(avail_df)}")
    print(f"Total puppies from pattern: {avail_df['extracted_count'].sum():,}")
    print(f"Average extracted: {avail_df['extracted_count'].mean():.1f}")
    print(f"Median extracted: {avail_df['extracted_count'].median():.0f}")
    print(f"\n⚠️ VALIDATION NEEDED: Check if these look like real puppy counts or parsing errors")
    print(f"Look for: prices >£500 in single extraction, years (2025/2026), suspicious patterns")
else:
    print("No extractions to validate")
