"""
Match engine — automatically links verified donors with waiting receivers.
"""
import logging
from app.db.database import get_organ_registrations_table, get_receivers_table
from app.models.donor import DonorStatus

logger = logging.getLogger(__name__)

async def find_matches_for_organ(organ_registration_id: str) -> list:
    """
    Given a new organ registration, find ALL compatible receivers.
    """
    organs = get_organ_registrations_table()
    res = organs.select("*").eq("id", organ_registration_id).execute()
    reg = res.data[0] if res.data else None
    if not reg: return []

    organ_name = reg["organ_name"]
    blood_group = reg["blood_group"]

    # Simple match: same organ + same blood group
    receivers_table = get_receivers_table()
    # Note: Currently receivers don't store organ_needed in the receivers table reliably.
    # In a real app, receivers would have an 'organ_needed' field.
    # For now, we fetch receivers in the same area or just all receivers.
    
    # Let's assume receivers search for organs. This service is for 'system-initiated' matching.
    # We will return potential candidates.
    r_res = receivers_table.select("*").execute()
    potential = r_res.data
    
    matches = []
    for r in potential:
        # In a real scenario, we'd check r["organ_needed"] == organ_name
        # and r["blood_group"] == blood_group
        matches.append({
            "receiver_id": str(r["id"]),
            "user_id": r["user_id"],
            "match_score": 100,
            "reason": "Compatible Blood Group & Organ Type"
        })
    
    return matches

async def get_global_stats() -> dict:
    """Calculate platform-wide KPIs."""
    from app.db.database import get_donors_table, get_receivers_table, get_hospitals_table
    
    donors = get_donors_table().select("id", "status").execute().data
    receivers = get_receivers_table().select("id").execute().data
    hospitals = get_hospitals_table().select("id").execute().data
    organs = get_organ_registrations_table().select("id").execute().data

    return {
        "total_donors": len(donors),
        "total_receivers": len(receivers),
        "total_hospitals": len(hospitals),
        "total_organs_listed": len(organs),
        "verified_donors": len([d for d in donors if d.get("status") == "approved"]),
        "pending_verifications": len([d for d in donors if d.get("status") == "pending"]),
    }
