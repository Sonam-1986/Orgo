import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Hit the PostgREST root to see available tables
headers = {"apikey": key, "Authorization": f"Bearer {key}"}
response = requests.get(f"{url}/rest/v1/", headers=headers)

if response.status_code == 200:
    print("Available tables/views:")
    data = response.json()
    if isinstance(data, dict) and "definitions" in data:
         for table in data["definitions"].keys():
             print(f"- {table}")
    else:
        # Sometimes it returns a different structure or just a list of tables
        print(data)
else:
    print(f"Failed to get table list: {response.status_code} - {response.text}")
