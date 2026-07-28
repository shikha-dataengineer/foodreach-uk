import requests
import pandas as pd

# Give Food free API - no key needed
url = "https://www.givefood.org.uk/api/2/locations/"

response = requests.get(url)
data = response.json()

# See what one food bank looks like
print(data[0])
print(f"\nTotal food banks: {len(data)}")

# Convert to a table
df = pd.DataFrame(data)
print(df[['name', 'postcode', 'country', 'network']].head(10))