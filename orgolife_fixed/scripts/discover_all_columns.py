import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_table_columns(table_name):
    print(f"\n--- Checking columns for '{table_name}' ---")
    try:
        # Intentionally selecting a non-existent column 'xyz_non_existent'
        # to trigger a PostgREST error that usually lists available columns.
        supabase.table(table_name).select("xyz_non_existent").limit(1).execute()
    except Exception as e:
        print(f"Error Message: {e}")

check_table_columns("donors")
check_table_columns("receivers")
check_table_columns("users")
check_table_columns("hospitals")
