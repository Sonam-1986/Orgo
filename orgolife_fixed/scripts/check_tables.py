import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

try:
    # Try to fetch from information_schema
    res = supabase.rpc("get_tables", {}).execute()
    print("Tables:", res.data)
except Exception as e:
    print("RPC failed, trying direct select on users")
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        print("Users table exists. Found:", len(res.data))
    except Exception as e2:
        print("Users table failed:", e2)

try:
    res = supabase.table("donors").select("*").limit(1).execute()
    print("Donors table exists.")
except Exception as e:
    print("Donors table failed:", e)
