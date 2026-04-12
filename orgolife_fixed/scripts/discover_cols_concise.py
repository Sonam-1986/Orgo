import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

for table in ["donors", "receivers"]:
    print(f"\nTABLE: {table}")
    try:
        # Trigger 'column does not exist' error to see available columns
        supabase.table(table).select("list_my_cols").limit(1).execute()
    except Exception as e:
        # Extract hint/message which usually contains column names in PostgREST
        print(f"ERROR: {e}")
