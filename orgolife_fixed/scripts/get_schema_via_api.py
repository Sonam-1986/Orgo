import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Supabase PostgREST root returns OpenAPI spec with table structures
api_url = f"{url}/rest/v1/"
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}"
}

try:
    print(f"Fetching OpenAPI spec from {api_url}...")
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        spec = response.json()
        definitions = spec.get("definitions", {})
        if "receivers" in definitions:
            print("\nColumns in 'receivers' table:")
            props = definitions["receivers"].get("properties", {})
            for prop in props:
                print(f"- {prop}")
        else:
            print("\n'receivers' not found in definitions.")
            
        if "donors" in definitions:
            print("\nColumns in 'donors' table:")
            props = definitions["donors"].get("properties", {})
            for prop in props:
                print(f"- {prop}")
    else:
        print(f"Failed to fetch spec. Status: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
