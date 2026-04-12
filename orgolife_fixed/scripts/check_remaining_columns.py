import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

tables = ["donors", "receivers", "hospitals"]

for table in tables:
    try:
        print(f"Checking columns in '{table}' table...")
        res = supabase.table(table).select("*").limit(1).execute()
        if res.data:
            print(f"Columns in {table}:", res.data[0].keys())
        else:
            print(f"No records in {table}, can't check columns easily via select(*).")
    except Exception as e:
        print(f"❌ Failed to fetch {table}: {e}")
