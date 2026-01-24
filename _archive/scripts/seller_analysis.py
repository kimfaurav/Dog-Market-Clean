import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', dtype={'seller_name': 'str'}, low_memory=False)
derived = pd.read_csv('output/views/derived.csv', dtype={'seller_name': 'str'}, low_memory=False)

top_sellers = facts['seller_name'].value_counts().head(15)

for seller, count in top_sellers.items():
    seller_data = facts[facts['seller_name'] == seller]
    breeds = seller_data['breed'].value_counts()
    platforms = seller_data['platform'].value_counts()
    
    print(f"\n{seller} - {count} listings")
    print(f"  Platforms: {list(platforms.index)}")
    print(f"  Top breed: {breeds.index[0]} ({breeds.iloc[0]}/{count})")
