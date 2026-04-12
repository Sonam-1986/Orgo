import os
import requests
from dotenv import load_dotenv
from supabase import create_client

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_receiver_registration():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    email = "receiver_test_flow@example.com"
    # Cleanup
    supabase.table("users").delete().eq("email", email).execute()

    print(f"\n--- Testing Receiver Registration Flow ({email}) ---")

    data = {
        "name": "Receiver Test Flow",
        "email": email,
        "password": "Password123!",
        "contact_number": "9988776655",
        "age": "45",
        "father_name": "Test Father R",
        "state": "Gujarat",
        "city": "Ahmedabad"
    }

    dummy_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref 0 4 0000000000 65535 f 0000000018 00000 n 0000000077 00000 n 0000000135 00000 n trailer<</Size 4/Root 1 0 R>>startxref 226 %%EOF"

    files = {
        "aadhaar_file": ("aadhaar_r.pdf", dummy_pdf, "application/pdf"),
        "pan_file": ("pan_r.pdf", dummy_pdf, "application/pdf"),
        "medical_file": ("medical_r.pdf", dummy_pdf, "application/pdf")
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register/receiver", data=data, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Receiver registration SUCCESSFUL!")
        else:
            print("❌ Receiver registration FAILED.")
    except Exception as e:
        print(f"❌ Error during receiver registration: {e}")

if __name__ == "__main__":
    test_receiver_registration()
