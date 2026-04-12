import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def debug_search():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    client = create_client(url, key)
    
    print(f"Testing connectivity to {url}...")
    try:
        # Simple count first
        res = client.table("organ_registrations").select("*", count="exact").limit(1).execute()
        print(f"Count of organs: {res.count}")
        
        # Test the exact query that failed (e.g. Kidney, A+, Maharashtra)
        print("Testing filtered query...")
        res = client.table("organ_registrations").select("*")\
            .eq("organ_name", "kidney")\
            .eq("blood_group", "A+")\
            .ilike("state", "%Maharashtra%")\
            .execute()
        print(f"Filtered result length: {len(res.data)}")
        
        if res.data:
            donor_id = res.data[0].get("donor_id")
            print(f"Testing donor fetch for {donor_id}...")
            d_res = client.table("donors").select("*").eq("id", donor_id).execute()
            print(f"Donor data found: {bool(d_res.data)}")

    except Exception as e:
        print(f"!!! Error caught: {e}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text[:500]}")

if __name__ == "__main__":
    asyncio.run(debug_search())
