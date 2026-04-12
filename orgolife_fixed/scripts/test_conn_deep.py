import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    print("Testing select(*) on users...")
    res = supabase.table("users").select("*").limit(1).execute()
    print(f"✅ Select successful! Found {len(res.data)} users.")
except Exception as e:
    print(f"❌ Select failed: {e}")

try:
    print("\nTesting select(count) on users...")
    res = supabase.table("users").select("id", count="exact").limit(1).execute()
    print(f"✅ Count successful! Count: {res.count}")
except Exception as e:
    print(f"❌ Count failed: {e}")
