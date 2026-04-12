import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

table = "receivers"
try:
    print(f"Checking columns in '{table}' table...")
    # Attempt to insert a dummy record with only one field and roll it back?
    # No, Supabase doesn't easily support rollbacks via client.
    # Instead, we can use the PostgREST /rpc endpoint or just try a dummy select.
    res = supabase.table(table).select("*").limit(0).execute()
    # This might not return column names if empty.
    
    # Let's try to query the information_schema via a raw SQL if we have service key? 
    # Usually anon key can't do that.
    
    # Another trick: try to select a non-existent column and see the error message.
    # It might list available columns.
except Exception as e:
    print(f"Error: {e}")

# Let's try to insert a minimal record and see what fails.
try:
    print("\nAttempting minimal insert into 'receivers'...")
    res = supabase.table(table).insert({"status": "pending"}).execute()
    print("Insert success (unexpected):", res.data)
except Exception as e:
    print(f"Insert failed: {e}")
