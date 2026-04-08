"""
Hospital model — stored in 'hospitals' collection.
Hospital Admins are linked here.
"""
from datetime import datetime, timezone
from typing import List, Optional


def hospital_document(
    name: str,
    admin_user_id: str,
    state: str,
    city: str,
    address: str,
    contact_number: str,
    registration_number: str,
    specializations: Optional[List[str]] = None,
) -> dict:
    """Factory for hospitals collection document."""
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "admin_user_id": admin_user_id,
        "address": {
            "state": state,
            "city": city,
            "full_address": address,
        },
        "contact_number": contact_number,
        "registration_number": registration_number,
        "specializations": specializations or [],
        "is_active": True,
        "total_approvals": 0,
        "total_rejections": 0,
        "created_at": now,
        "updated_at": now,
    }
