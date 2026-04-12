import os
from dotenv import load_dotenv
from supabase import create_client
from app.models.user import user_document, UserRole
from app.utils.password import hash_password

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

email = "manual_test@example.com"
# Cleanup
supabase.table("users").delete().eq("email", email).execute()

doc = user_document(
    name="Manual Test",
    email=email,
    hashed_password=hash_password("Password123!"),
    role=UserRole.USER,
    contact_number="1234567890"
)

try:
    res = supabase.table("users").insert(doc).execute()
    print("Insertion successful! ID:", res.data[0]["id"])
except Exception as e:
    print("Insertion failed:", e)
