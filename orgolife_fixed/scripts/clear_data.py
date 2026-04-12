import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clear_data():
    print("WARNING: Deleting all existing user data from Supabase...")
    
    try:
        # We can delete all records by deleting where id is not null.
        # supabase python client format: supabase.table("table_name").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        # A simpler way is just to use .neq("id", "-1") or similar, as UUIDs don't match it.
        # Alternatively, we can just delete from `users` which might cascade, but let's be thorough.
        
        print("Clearing organ_registrations...")
        supabase.table("organ_registrations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        print("Clearing receivers...")
        supabase.table("receivers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        print("Clearing donors...")
        supabase.table("donors").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        print("Clearing users...")
        supabase.table("users").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        print("Clearing hospitals...")
        supabase.table("hospitals").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        print("Successfully cleared all platform data. Database is now fresh.")
        
    except Exception as e:
        print(f"Error while clearing data: {e}")

if __name__ == "__main__":
    clear_data()
