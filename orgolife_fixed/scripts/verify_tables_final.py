import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

for table in ["users", "donors", "receivers", "hospitals"]:
    try:
        res = supabase.table(table).select("count", count="exact").limit(1).execute()
        print(f"✅ Table '{table}' exists.")
    except Exception as e:
        print(f"❌ Table '{table}' failed: {e}")
