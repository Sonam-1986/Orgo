import os
import sys
import time
import requests
import subprocess
from dotenv import load_dotenv
from supabase import create_client

# Define the base URL for the API
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test user data
TEST_USER = {
    "email": "test_verification_user@example.com",
    "password": "Password123!",
    "name": "Verification User",
    "contact_number": "1234567890",
    "role": "donor"
}

def start_server():
    print("🚀 Starting FastAPI server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Wait for server to start
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                print("✅ Server is up and running!")
                return process
        except Exception:
            pass
        time.sleep(2)
        print(f"Waiting for server... ({i+1}/{max_retries})")
    
    print("❌ Failed to start server.")
    process.terminate()
    sys.exit(1)

def run_tests():
    load_dotenv()
    
    print("\n--- Starting Verification Tests ---")
    
    # 1. Register User
    print(f"Step 1: Registering user {TEST_USER['email']}...")
    try:
        # Check if user already exists in DB to prevent unique constraint error
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase = create_client(url, key)
        
        # Cleanup if exists
        supabase.table("users").delete().eq("email", TEST_USER["email"]).execute()
        
        # Register via API
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 201:
            print("✅ Registration successful (API returned 201).")
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
            print("✅ Login successful, token received.")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

    # 3. Fetch Profile (Me)
    print("Step 3: Fetching user profile...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json().get("data")
            if user_info and user_info.get("email") == TEST_USER["email"]:
                print(f"✅ Profile fetch successful for {user_info.get('name')}.")
            else:
                print(f"❌ Profile data mismatch: {user_info}")
                return False
        else:
            print(f"❌ Profile fetch failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during profile fetch: {e}")
        return False

    # 4. Confirm in Supabase
    print("Step 4: Confirming data in Supabase database...")
    try:
        res = supabase.table("users").select("*").eq("email", TEST_USER["email"]).execute()
        if len(res.data) > 0:
            db_user = res.data[0]
            print(f"✅ User found in Supabase! ID: {db_user.get('id')}")
            print(f"   Name: {db_user.get('full_name')}")
            print(f"   Role: {db_user.get('role')}")
            return True
        else:
            print("❌ User NOT found in Supabase table.")
            return False
    except Exception as e:
        print(f"❌ Error querying Supabase: {e}")
        return False

if __name__ == "__main__":
    server_process = start_server()
    success = False
    try:
        success = run_tests()
    finally:
        print("\n--- Cleaning Up ---")
        server_process.terminate()
        print("🛑 Server stopped.")
    
    if success:
        print("\n🚀 ALL TESTS PASSED SUCCESSFULLY! The program is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED. Please check the logs.")
        sys.exit(1)
