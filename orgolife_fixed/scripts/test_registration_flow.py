import os
import requests
import time
from dotenv import load_dotenv
from supabase import create_client

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_donor_registration():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    email = "donor_test_flow@example.com"
    # Cleanup
    supabase.table("users").delete().eq("email", email).execute()

    print(f"\n--- Testing Donor Registration Flow ({email}) ---")

    # Prepare multipart/form-data
    data = {
        "name": "Donor Test Flow",
        "email": email,
        "password": "Password123!",
        "contact_number": "1122334455",
        "age": "30",
        "father_name": "Test Father",
        "state": "Maharashtra",
        "city": "Mumbai",
        "full_address": "123 Test St, Mumbai",
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE1234F"
    }

    # Dummy PDF content
    dummy_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref 0 4 0000000000 65535 f 0000000018 00000 n 0000000077 00000 n 0000000135 00000 n trailer<</Size 4/Root 1 0 R>>startxref 226 %%EOF"

    files = {
        "aadhaar_file": ("aadhaar.pdf", dummy_pdf, "application/pdf"),
        "pan_file": ("pan.pdf", dummy_pdf, "application/pdf"),
        "medical_file": ("medical.pdf", dummy_pdf, "application/pdf")
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register/donor", data=data, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Donor registration SUCCESSFUL!")
            
            # Check if user exists
            res = supabase.table("users").select("*").eq("email", email).execute()
            if res.data:
                print(f"✅ User record found in Supabase. ID: {res.data[0]['id']}")
                
                # Check if donor profile exists
                donor_res = supabase.table("donors").select("*").eq("user_id", res.data[0]['id']).execute()
                if donor_res.data:
                    print("✅ Donor profile record found in Supabase.")
                else:
                    print("❌ Donor profile record MISSING in Supabase.")
            else:
                print("❌ User record MISSING in Supabase.")
        else:
            print("❌ Donor registration FAILED.")

    except Exception as e:
        print(f"❌ Error during donor registration: {e}")

if __name__ == "__main__":
    test_donor_registration()
