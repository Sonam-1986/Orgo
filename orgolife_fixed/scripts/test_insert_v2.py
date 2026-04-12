import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client
from app.models.user import user_document, UserRole, UserStatus
from app.utils.password import hash_password

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

email = "manual_test_v2@example.com"
supabase.table("users").delete().eq("email", email).execute()

doc = user_document(
    name="Manual Test V2",
    email=email,
    hashed_password=hash_password("Password123!"),
    role=UserRole.USER,
    contact_number="1234567890"
)

print("Document to insert:")
print(doc)

try:
    print("\nTesting insert on users...")
    # Manually ensure everything is strings
    clean_doc = {k: str(v) if not isinstance(v, (bool, int, float)) and v is not None else v for k, v in doc.items()}
    res = supabase.table("users").insert(clean_doc).execute()
    print("✅ Insertion successful! ID:", res.data[0]["id"])
except Exception as e:
    print("❌ Insertion failed:", e)
