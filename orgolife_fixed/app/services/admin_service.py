"""
Hospital Admin service — donor listing, document access, verification actions.
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.database import (
    get_users_collection, get_donors_collection,
    get_hospitals_collection, get_organ_registrations_collection
)
from app.models.donor import DonorStatus
from app.services.file_service import file_url
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


async def _get_hospital_for_admin(admin_user_id: str) -> dict:
    """Fetch the hospital linked to this admin. Raises 404 if missing."""
    hospitals = get_hospitals_collection()
    hospital = await hospitals.find_one({"admin_user_id": admin_user_id})
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this admin account."
        )
    return hospital


# ── Donor Listing ─────────────────────────────────────────────────

async def list_all_donors(
    admin_user_id: str,
    page: int = 1,
    page_size: int = 10,
    status_filter: str = "all",
) -> dict:
    """
    Paginated donor list visible to hospital admins.
    Optionally filtered by verification status.
    """
    await _get_hospital_for_admin(admin_user_id)  # auth check

    donors_col = get_donors_collection()
    users_col = get_users_collection()

    query = {}
    if status_filter != "all":
        query["status"] = status_filter

    skip = (page - 1) * page_size
    total = await donors_col.count_documents(query)
    cursor = donors_col.find(query).sort("created_at", -1).skip(skip).limit(page_size)

    items = []
    async for donor in cursor:
        user = await users_col.find_one({"_id": ObjectId(donor["user_id"])})
        if not user:
            continue

        docs = donor.get("documents", {})
        items.append({
            "donor_id": str(donor["_id"]),
            "user_id": donor["user_id"],
            "name": user["name"],
            "email": user["email"],
            "age": donor["age"],
            "contact_number": user["contact_number"],
            "state": donor["address"]["state"],
            "city": donor["address"]["city"],
            "verified": donor["verified"],
            "status": donor["status"],
            "aadhaar_card_url": file_url(docs.get("aadhaar_card_path", "")),
            "pan_card_url": file_url(docs.get("pan_card_path", "")),
            "medical_report_url": file_url(docs.get("medical_report_path", "")),
            "created_at": donor["created_at"].isoformat(),
        })

    return paginate_response(items, total, page, page_size)


# ── Full Donor Detail ─────────────────────────────────────────────

async def get_donor_detail(admin_user_id: str, donor_id: str) -> dict:
    """Return complete donor info (including unmasked docs) for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    donors_col = get_donors_collection()
    try:
        donor = await donors_col.find_one({"_id": ObjectId(donor_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid donor_id format.")

    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found.")

    users_col = get_users_collection()
    user = await users_col.find_one({"_id": ObjectId(donor["user_id"])})

    organs_col = get_organ_registrations_collection()
    organs_cursor = organs_col.find({"donor_id": donor_id})
    organs = []
    async for o in organs_cursor:
        organs.append({
            "registration_id": str(o["_id"]),
            "organ_name": o["organ_name"],
            "blood_group": o["blood_group"],
            "health_report": o["health_report"],
            "hospitals_selected": o["hospitals_selected"],
            "state": o["state"],
            "city": o["city"],
            "is_available": o["is_available"],
        })

    docs = donor.get("documents", {})
    return {
        "donor_id": donor_id,
        "user_id": donor["user_id"],
        "name": user["name"],
        "email": user["email"],
        "age": donor["age"],
        "father_name": donor["father_name"],
        "contact_number": user["contact_number"],
        "state": donor["address"]["state"],
        "city": donor["address"]["city"],
        "full_address": donor["address"]["full_address"],
        "aadhaar_number": donor.get("aadhaar_number", "N/A"),
        "pan_number": donor.get("pan_number", "N/A"),
        "verified": donor["verified"],
        "status": donor["status"],
        "rejection_reason": donor.get("rejection_reason"),
        "verified_by_hospital": donor.get("verified_by_hospital"),
        "aadhaar_card_url": file_url(docs.get("aadhaar_card_path", "")),
        "pan_card_url": file_url(docs.get("pan_card_path", "")),
        "medical_report_url": file_url(docs.get("medical_report_path", "")),
        "organ_registrations": organs,
        "created_at": donor["created_at"].isoformat(),
    }


# ── Approve Donor ─────────────────────────────────────────────────

async def approve_donor(admin_user_id: str, donor_id: str, notes: str = None) -> dict:
    """
    Set donor.verified=True, donor.status='approved'.
    Tag with hospital name for audit trail.
    """
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital["name"]

    donors_col = get_donors_collection()
    try:
        oid = ObjectId(donor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid donor_id format.")

    donor = await donors_col.find_one({"_id": oid})
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found.")

    if donor["status"] == DonorStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Donor is already approved.")

    now = datetime.now(timezone.utc)
    await donors_col.update_one(
        {"_id": oid},
        {"$set": {
            "verified": True,
            "status": DonorStatus.APPROVED,
            "verified_by_hospital": hospital_name,
            "verified_by_admin_id": admin_user_id,
            "rejection_reason": None,
            "approval_notes": notes,
            "updated_at": now,
        }}
    )

    # Increment hospital approval counter
    hospitals_col = get_hospitals_collection()
    await hospitals_col.update_one(
        {"_id": hospital["_id"]},
        {"$inc": {"total_approvals": 1}, "$set": {"updated_at": now}}
    )

    logger.info(f"Donor APPROVED: donor_id={donor_id} | by hospital={hospital_name}")
    return {
        "donor_id": donor_id,
        "new_status": DonorStatus.APPROVED,
        "verified": True,
        "action_by_hospital": hospital_name,
        "message": "Donor has been approved and is now visible in search results.",
    }


# ── Reject Donor ──────────────────────────────────────────────────

async def reject_donor(admin_user_id: str, donor_id: str, rejection_reason: str) -> dict:
    """
    Set donor.verified=False, donor.status='rejected'.
    Store the rejection reason.
    """
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital["name"]

    donors_col = get_donors_collection()
    try:
        oid = ObjectId(donor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid donor_id format.")

    donor = await donors_col.find_one({"_id": oid})
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found.")

    if donor["status"] == DonorStatus.REJECTED:
        raise HTTPException(status_code=409, detail="Donor is already rejected.")

    now = datetime.now(timezone.utc)
    await donors_col.update_one(
        {"_id": oid},
        {"$set": {
            "verified": False,
            "status": DonorStatus.REJECTED,
            "rejection_reason": rejection_reason,
            "verified_by_hospital": hospital_name,
            "verified_by_admin_id": admin_user_id,
            "updated_at": now,
        }}
    )

    hospitals_col = get_hospitals_collection()
    await hospitals_col.update_one(
        {"_id": hospital["_id"]},
        {"$inc": {"total_rejections": 1}, "$set": {"updated_at": now}}
    )

    logger.info(f"Donor REJECTED: donor_id={donor_id} | hospital={hospital_name}")
    return {
        "donor_id": donor_id,
        "new_status": DonorStatus.REJECTED,
        "verified": False,
        "action_by_hospital": hospital_name,
        "message": "Donor registration has been rejected.",
    }


# ── Admin's Hospital Profile ──────────────────────────────────────

async def get_hospital_profile(admin_user_id: str) -> dict:
    """Return the hospital profile for the logged-in admin."""
    hospital = await _get_hospital_for_admin(admin_user_id)
    return {
        "hospital_id": str(hospital["_id"]),
        "name": hospital["name"],
        "state": hospital["address"]["state"],
        "city": hospital["address"]["city"],
        "registration_number": hospital["registration_number"],
        "total_approvals": hospital.get("total_approvals", 0),
        "total_rejections": hospital.get("total_rejections", 0),
        "created_at": hospital["created_at"].isoformat(),
    }
