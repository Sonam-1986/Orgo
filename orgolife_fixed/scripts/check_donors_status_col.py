import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

table = "donors"
try:
    print(f"Testing select(status) on '{table}'...")
    res = supabase.table(table).select("status").limit(1).execute()
    print(f"✅ Select(status) success! Found {len(res.data)} records.")
except Exception as e:
    print(f"❌ Select(status) failed: {e}")
