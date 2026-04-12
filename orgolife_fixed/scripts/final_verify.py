"""
Full system verification: DB connectivity, user registration, data persistence.
"""
import requests
import time
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
BASE = "http://127.0.0.1:8002/api/v1"

print("=" * 55)
print("  ORGOLIFE SYSTEM VERIFICATION")
print("=" * 55)

# 1. Health check
try:
    r = requests.get("http://127.0.0.1:8002/health", timeout=5)
    print(f"[1] Server health:     {r.status_code} - {r.json()}")
except Exception as e:
    print(f"[1] Server health:     FAILED - {e}")

# 2. Register a fresh test user
ts = int(time.time())
email = f"verify_{ts}@test.com"
try:
    r = requests.post(f"{BASE}/auth/register", json={
        "name": "Verify User",
        "email": email,
        "password": "Test@1234",
        "contact_number": "9000000001"
    }, timeout=10)
    uid = r.json().get("data", {}).get("user_id", "N/A")
    print(f"[2] Register user:     {r.status_code} - user_id={uid}")
except Exception as e:
    print(f"[2] Register user:     FAILED - {e}")

# 3. Login with that user
try:
    r2 = requests.post(f"{BASE}/auth/login", json={
        "email": email,
        "password": "Test@1234"
    }, timeout=10)
    token = r2.json().get("access_token", "")
    print(f"[3] Login:             {r2.status_code} - token={'OK' if token else 'FAILED'}")
except Exception as e:
    print(f"[3] Login:             FAILED - {e}")
    token = ""

# 4. Verify the user landed in Supabase DB
try:
    sb_url = os.getenv("SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_KEY")
    sb = create_client(sb_url, sb_key)
    res = sb.table("users").select("id,name,email,role,status").eq("email", email).execute()
    if res.data:
        u = res.data[0]
        print(f"[4] DB check (users):  STORED - name={u['name']}, role={u['role']}, status={u['status']}")
    else:
        print("[4] DB check (users):  NOT FOUND in Supabase!")
except Exception as e:
    print(f"[4] DB check:          ERROR - {e}")

# 5. Count total users in DB
try:
    all_users = sb.table("users").select("id").execute()
    print(f"[5] Total users in DB: {len(all_users.data)}")
except Exception as e:
    print(f"[5] Total users:       ERROR - {e}")

# 6. Count donors
try:
    donors = sb.table("donors").select("id").execute()
    print(f"[6] Total donors in DB:{len(donors.data)}")
except Exception as e:
    print(f"[6] Total donors:      ERROR - {e}")

# 7. Count receivers
try:
    receivers = sb.table("receivers").select("id").execute()
    print(f"[7] Total receivers:   {len(receivers.data)}")
except Exception as e:
    print(f"[7] Total receivers:   ERROR - {e}")

# 8. Check authenticated profile fetch
if token:
    try:
        h = {"Authorization": f"Bearer {token}"}
        rp = requests.get(f"{BASE}/auth/me", headers=h, timeout=5)
        print(f"[8] Auth /me:          {rp.status_code} - {rp.json()}")
    except Exception as e:
        print(f"[8] Auth /me:          ERROR - {e}")

print("=" * 55)
print("  VERIFICATION COMPLETE")
print("=" * 55)
