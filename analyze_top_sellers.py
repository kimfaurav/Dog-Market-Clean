import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', low_memory=False)
derived = pd.read_csv('output/views/derived.csv', low_memory=False)

# Get top sellers
top_sellers = facts['seller_name'].value_counts().head(20)

print("TOP SELLERS - DETAILED ANALYSIS\n")
print("=" * 100)

suspicious_sellers = []

for seller, count in top_sellers.items():
    if pd.isna(seller) or seller == '':
        continue
    
    seller_data = facts[facts['seller_name'] == seller]
    seller_derived = derived[derived['seller_name'] == seller]
    
    # Get platforms
    platforms = seller_data['platform'].value_counts()
    
    # Get breeds
    breeds = seller_data['breed'].value_counts()
    
    # Get price range
    prices = seller_derived['price_num'].dropna()
    
    print(f"\n{seller.ljust(40)} - {count} listings")
    print(f"  Platforms: {', '.join([f'{p}({c})' for p, c in platforms.items()])}")
    if len(prices) > 0:
        print(f"  Price range: £{prices.min():.0f} - £{prices.max():.0f} (avg: £{prices.mean():.0f})")
    print(f"  Top breeds: {', '.join([f'{b}({c})' for b, c in breeds.head(3).items()])}")
    
    # Red flags
    red_flags = []
    
    # All same breed = reseller/broker
    if len(breeds) > 0 and breeds.iloc[0] > count * 0.7:
        red_flags.append(f"Mostly {breeds.index[0]} ({breeds.iloc[0]}/{count})")
    
    # Very wide price range
    if len(prices) > 1 and prices.max() / prices.min() > 5:
        red_flags.append(f"Price variation {prices.max()/prices.min():.0f}x")
    
    # All from one platform
    if len(platforms) == 1:
        red_flags.append(f"Only {platforms.index[0]}")
    
    # Generic/numeric name
    if len(seller) <= 5 or seller.isdigit():
        red_flags.append("Generic name")
    
    if red_flags:
        print(f"  🚩 {', '.join(red_flags)}")
        suspicious_sellers.append(seller)
    else:
        print(f"  ✓ OK")

print("\n" + "=" * 100)
print(f"\nSUSPICIOUS SELLERS: {len(suspicious_sellers)}")
for seller in suspicious_sellers:
    print(f"  • {seller}")
