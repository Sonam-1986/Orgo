import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    print("Fetching one record from users to check columns...")
    res = supabase.table("users").select("*").limit(1).execute()
    if res.data:
        print("Columns in data:", res.data[0].keys())
    else:
        print("No records found in users.")
except Exception as e:
    print(f"❌ Failed to fetch: {e}")
