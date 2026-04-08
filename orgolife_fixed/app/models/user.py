"""
User model — shared base for Donor, Receiver, Hospital Admin.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from bson import ObjectId


class UserRole(str, Enum):
    DONOR = "donor"
    RECEIVER = "receiver"
    HOSPITAL_ADMIN = "hospital_admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


def user_document(
    name: str,
    email: str,
    hashed_password: str,
    role: UserRole,
    contact_number: str,
) -> dict:
    """Factory — returns a ready-to-insert MongoDB user document."""
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "email": email.lower().strip(),
        "password": hashed_password,
        "role": role,
        "contact_number": contact_number,
        "status": UserStatus.ACTIVE,
        "is_verified_email": False,
        "created_at": now,
        "updated_at": now,
    }
