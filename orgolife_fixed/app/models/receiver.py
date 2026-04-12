"""
Receiver model — stored in 'receivers' table.

NOTE: Only includes columns that are confirmed to exist in the Supabase DB.
      Run the ALTER TABLE script in supabase_schema.sql to add optional columns.
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
    organ_name: Optional[str] = None,
    aadhaar_number: Optional[str] = None,
    pan_number: Optional[str] = None,
) -> dict:
    """Factory for receivers table — only uses columns known to exist in DB."""
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": user_id,
        "age": age,
        "father_name": father_name,
        "state": state,
        "city": city,
        "aadhaar_card_path": aadhaar_card_path,
        "pan_card_path": pan_card_path,
        "medical_report_path": medical_report_path,
        "organ_name": organ_name,
        "aadhaar_number": aadhaar_number,
        "pan_number": pan_number,
        "created_at": now,
        "updated_at": now,
    }
    return doc
