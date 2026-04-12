import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    print("Fetching last registered donor...")
    res = supabase.table("donors").select("*").order("created_at", desc=True).limit(1).execute()
    if res.data:
        donor = res.data[0]
        print("Donor columns found:", list(donor.keys()))
        print("Donor data:", donor)
    else:
        print("No donors found.")
except Exception as e:
    print(f"Error fetching donors: {e}")

try:
    print("\nFetching last registered user...")
    res = supabase.table("users").select("*").order("created_at", desc=True).limit(1).execute()
    if res.data:
        user = res.data[0]
        print("User columns found:", list(user.keys()))
    else:
        print("No users found.")
except Exception as e:
    print(f"Error fetching users: {e}")
