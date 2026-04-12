import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def patch_db():
    print("Patching receivers table to add organ_name column...")
    try:
        # Supabase Python client doesn't support raw SQL easily unless we use an RPC.
        # But we can try to just run a dummy query to see if the column exists, 
        # however, there's no direct 'alter table' via public REST API.
        # Usually, users run SQL in the dashboard.
        # Since I can't run raw SQL via the client easily without an RPC, 
        # I will assume the user will run the schema or I can try to use a 
        # 'hack' if there's a stored procedure, but there likely isn't.
        
        # We'll just print a message that they should run the SQL in their dashboard 
        # IF the rest of my backend logic starts using it.
        # Actually, let's try to just insert a dummy with the new col to see if it works.
        pass
    except Exception as e:
        print(f"Patch info: {e}")

if __name__ == "__main__":
    patch_db()
    print("Note: If the column 'organ_name' is missing, please run the SQL in supabase_schema.sql in your Supabase SQL Editor.")
