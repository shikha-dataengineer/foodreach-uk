import requests
import pandas as pd

# Give Food free API - no key needed
url = "https://www.givefood.org.uk/api/2/locations/"

response = requests.get(url)
data = response.json()

print(f"Total locations: {len(data)}")

# Fix: extract nested fields correctly
rows = []
for item in data:
    rows.append({
        "name": item.get("name", ""),
        "postcode": item.get("postcode", ""),
        "network": item["foodbank"].get("network", ""),
        "foodbank_name": item["foodbank"].get("name", ""),
        "lat_lng": item.get("lat_lng", ""),
        "address": item.get("address", "").replace("\r\n", ", ").replace("\n", ", ")
    })

df = pd.DataFrame(rows)
print(df.head(10))
print(f"\nNetworks breakdown:")
print(df["network"].value_counts())
