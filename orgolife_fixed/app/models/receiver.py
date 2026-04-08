"""
Receiver model — stored in 'receivers' collection.
"""
from datetime import datetime, timezone
from typing import Optional


def receiver_document(
    user_id: str,
    age: int,
    father_name: str,
    state: str,
    city: str,
    aadhaar_card_path: str,
    pan_card_path: str,
    medical_report_path: str,
    aadhaar_number: Optional[str] = None,
    pan_number: Optional[str] = None,
) -> dict:
    """Factory for receivers collection document."""
    now = datetime.now(timezone.utc)
    return {
        "user_id": user_id,
        "age": age,
        "father_name": father_name,
        "location": {
            "state": state,
            "city": city,
        },
        "documents": {
            "aadhaar_card_path": aadhaar_card_path,
            "pan_card_path": pan_card_path,
            "medical_report_path": medical_report_path,
        },
        "aadhaar_number": aadhaar_number,
        "pan_number": pan_number,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
