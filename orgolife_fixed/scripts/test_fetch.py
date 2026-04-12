import requests
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
ts = str(uuid.uuid4())[:8]

# 1. Register and Login Admin
admin_email = f"admin_fetch_{ts}@example.com"
admin_data = {
    "name": "Admin Fetch",
    "email": admin_email,
    "password": "Test@1234",
    "contact_number": "9000000001",
    "hospital_name": "Apollo Hospital Mumbai",
    "hospital_registration_number": f"REG-HOSP-{ts}",
    "hospital_state": "Maharashtra",
    "hospital_city": "Mumbai",
    "hospital_address": "Test Street 123",
    "hospital_contact": "022-12345678"
}
requests.post(f"{BASE}/auth/register/admin", data=admin_data)

login_res = requests.post(f"{BASE}/auth/login", json={"email": admin_email, "password": "Test@1234"})
token = login_res.json().get("access_token")

# 2. Fetch all donors
h = {"Authorization": f"Bearer {token}"}
res = requests.get(f"{BASE}/admin/donors", headers=h)
print(f"Admin Donors: {res.status_code}")
if res.status_code != 200:
    print(res.text)

# 3. Fetch all receivers
res = requests.get(f"{BASE}/admin/receivers", headers=h)
print(f"Admin Receivers: {res.status_code}")
if res.status_code != 200:
    print(res.text)

# 4. Fetch dashboard stats
res = requests.get(f"{BASE}/admin/stats", headers=h)
print(f"Admin stats: {res.status_code}")
if res.status_code != 200:
    print(res.text)
