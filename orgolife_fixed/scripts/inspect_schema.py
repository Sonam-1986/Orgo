"""
Inspect Supabase table schemas by checking existing rows.
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb = create_client(url, key)

def inspect(table_name):
    print(f"\n--- {table_name} ---")
    res = sb.table(table_name).select("*").limit(1).execute()
    if res.data:
        cols = list(res.data[0].keys())
        print(f"Columns: {cols}")
    else:
        print("Table is empty. Checking schema cache by sending invalid column...")
        try:
            sb.table(table_name).insert({"non_existent_field_diag": "1"}).execute()
        except Exception as e:
            # The error message usually list allowed columns
            print(f"Diagnostic error: {str(e)}")

for t in ["donors", "receivers", "hospitals", "users"]:
    inspect(t)
