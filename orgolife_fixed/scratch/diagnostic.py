import os
import sys
from dotenv import load_dotenv
from supabase import create_client

def test():
    print("--- START DIAGNOSTIC ---")
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return

    print(f"Connecting to: {url}")
    try:
        client = create_client(url, key)
        print("Client created. Fetching health...")
        
        # Test basic table fetch
        res = client.table("users").select("count", count="exact").limit(0).execute()
        print(f"Users count: {res.count}")
        
        # Test organ registrations fetch
        res = client.table("organ_registrations").select("*").limit(1).execute()
        print(f"Organs sample: {res.data}")
        
        print("Diagnostic SUCCESS")
    except Exception as e:
        print(f"!!! DIAGNOSTIC FAILED: {str(e)}")
        if hasattr(e, 'response'):
             print(f"Response Body: {e.response.text}")

if __name__ == "__main__":
    test()
