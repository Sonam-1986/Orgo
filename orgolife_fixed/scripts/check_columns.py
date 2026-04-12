import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Prefer": "return=minimal"
}

# Get columns of the users table
# Actually, PostgREST can give us the OpenAPI spec which lists columns
response = requests.get(f"{url}/rest/v1/", headers=headers)
if response.status_code == 200:
    definitions = response.json().get("definitions", {})
    users_def = definitions.get("users", {})
    properties = users_def.get("properties", {})
    print("Columns in 'users' table:")
    for col in properties.keys():
        print(f"- {col}")
else:
    print(f"Failed to get table info: {response.status_code}")
