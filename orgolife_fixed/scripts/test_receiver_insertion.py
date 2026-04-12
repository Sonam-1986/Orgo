import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# 1. Create a dummy user first (required by FK)
user_id = str(uuid.uuid4())
try:
    print(f"Creating dummy user {user_id}...")
    supabase.table("users").insert({
        "id": user_id,
        "email": f"test_receiver_{user_id[:8]}@example.com",
        "full_name": "Test Receiver",
        "role": "receiver"
    }).execute()
except Exception as e:
    print(f"User creation failed (might already exist or schema issue): {e}")

# 2. Try minimal insert into receivers
print("\nAttempting minimal insert into 'receivers'...")
try:
    res = supabase.table("receivers").insert({
        "user_id": user_id,
        "age": 30,
        "father_name": "Test Father",
        "state": "Test State",
        "city": "Test City"
    }).execute()
    print("✅ Minimal insert success!")
    print("Record:", res.data)
except Exception as e:
    print(f"❌ Minimal insert failed: {e}")

# 3. Try adding 'status'
print("\nAttempting insert with 'status' into 'receivers'...")
try:
    supabase.table("receivers").insert({
        "user_id": str(uuid.uuid4()), # New ID
        "age": 30,
        "status": "pending"
    }).execute()
    print("✅ Status insert success!")
except Exception as e:
    print(f"❌ Status insert failed: {e}")
