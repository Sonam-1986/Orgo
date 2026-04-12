import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client

# Use port 8001 as started manually
BASE_URL = "http://127.0.0.1:8001/api/v1"

TEST_USER = {
    "email": "api_test_user@example.com",
    "password": "Password123!",
    "name": "API Test User",
    "contact_number": "9876543210",
    "role": "donor"
}

def run_tests():
    load_dotenv()
    
    print("\n--- Starting API Verification Tests ---")
    
    # Check health
    try:
        res = requests.get("http://127.0.0.1:8001/health")
        print(f"Health check: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False

    # Supabase connection
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    # 1. Register User
    print(f"Step 1: Registering user {TEST_USER['email']}...")
    try:
        # Cleanup
        supabase.table("users").delete().eq("email", TEST_USER["email"]).execute()
        
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 201:
            print("✅ Registration successful.")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False

    # 2. Login
    print("Step 2: Logging in...")
    try:
        login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful.")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

    # 3. Fetch Profile
    print("Step 3: Fetching profile...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json().get("data")
            print(f"✅ Profile fetch successful for {user_info.get('full_name')}.")
        else:
            print(f"❌ Profile fetch failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during profile fetch: {e}")
        return False

    # 4. Confirm in Supabase
    print("Step 4: Confirming in Supabase...")
    try:
        res = supabase.table("users").select("*").eq("email", TEST_USER["email"]).execute()
        if len(res.data) > 0:
            print(f"✅ Success! User found in Supabase table.")
            return True
        else:
            print("❌ User NOT found in Supabase.")
            return False
    except Exception as e:
        print(f"❌ Error querying Supabase: {e}")
        return False

if __name__ == "__main__":
    if run_tests():
        print("\n🚀 VERIFICATION COMPLETED: All systems operational.")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED.")
        sys.exit(1)
