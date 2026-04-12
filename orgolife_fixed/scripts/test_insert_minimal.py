import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

email = "minimal_test@example.com"
supabase.table("users").delete().eq("email", email).execute()

doc = {
    "name": "Minimal Test",
    "email": email,
    "password": "hashed_stuff"
}

try:
    print("Testing minimal insert on users...")
    res = supabase.table("users").insert(doc).execute()
    print("✅ Insertion successful! ID:", res.data[0]["id"])
except Exception as e:
    print("❌ Insertion failed:", e)
