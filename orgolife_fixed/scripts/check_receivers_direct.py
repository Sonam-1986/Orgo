import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    print("Testing select(*) on receivers...")
    res = supabase.table("receivers").select("*").limit(1).execute()
    print(f"✅ Select successful! Found {len(res.data)} receivers.")
except Exception as e:
    print(f"❌ Select failed: {e}")
