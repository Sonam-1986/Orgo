"""
Hospital Admin service — donor listing, document access, verification actions.
"""
import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.db.database import (
    get_users_table, get_donors_table, get_receivers_table,
    get_hospitals_table, get_organ_registrations_table
)
from app.models.donor import DonorStatus
from app.services.file_service import get_signed_url
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


async def _get_hospital_for_admin(admin_user_id: str) -> dict:
    """Fetch the hospital linked to this admin. Checks user.hospital_id first."""
    users_table = get_users_table()
    u_res = users_table.select("hospital_id").eq("id", admin_user_id).execute()
    user = u_res.data[0] if u_res.data else {}
    
    hospital_id = user.get("hospital_id")
    hospitals = get_hospitals_table()

    if hospital_id:
        res = hospitals.select("*").eq("id", hospital_id).execute()
    else:
        # Fallback to legacy admin_user_id link
        res = hospitals.select("*").eq("admin_user_id", admin_user_id).execute()
    
    hospital = res.data[0] if res.data else None
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this admin account."
        )
    return hospital


def _safe_user_name(user: dict) -> str:
    """Return the name from a user record whether it's stored as 'name' or 'full_name'."""
    if not user:
        return ""
    return user.get("name") or user.get("full_name", "")


# ── Donor Listing ─────────────────────────────────────────────────

async def list_all_donors(
    admin_user_id: str,
    page: int = 1,
    page_size: int = 10,
    status_filter: str = "all",
) -> dict:
    """Paginated donor list visible to hospital admins."""
    await _get_hospital_for_admin(admin_user_id)  # auth check

    donors_table = get_donors_table()
    users_table = get_users_table()

    query = donors_table.select("*")
    if status_filter != "all":
        query = query.eq("status", status_filter)

    skip = (page - 1) * page_size
    total_res = query.execute()
    total = len(total_res.data)

    response = query.order("created_at", desc=True).range(skip, skip + page_size - 1).execute()
    donors = response.data

    items = []
    for donor in donors:
        u_res = users_table.select("*").eq("id", donor["user_id"]).execute()
        user = u_res.data[0] if u_res.data else None
        if not user:
            continue

        items.append({
            "donor_id": str(donor["id"]),
            "user_id": donor["user_id"],
            "name": _safe_user_name(user),
            "email": user.get("email", ""),
            "age": donor.get("age"),
            "contact_number": user.get("contact_number", ""),
            "father_name": donor.get("father_name", ""),
            "state": donor.get("state", ""),
            "city": donor.get("city", ""),
            "verified": donor.get("verified", False),
            "status": donor.get("status", "pending"),
            "organ_name": (get_organ_registrations_table().select("organ_name").eq("donor_id", str(donor["id"])).limit(1).execute().data or [{}])[0].get("organ_name", "N/A"),
            "aadhaar_card_url": get_signed_url("aadhaar", donor.get("aadhaar_card_path", "")),
            "pan_card_url": get_signed_url("pan", donor.get("pan_card_path", "")),
            "medical_report_url": get_signed_url("medical", donor.get("medical_report_path", "")),
            "created_at": donor.get("created_at"),
        })

    return paginate_response(items, total, page, page_size)


# ── Full Donor Detail ─────────────────────────────────────────────

async def get_donor_detail(admin_user_id: str, donor_id: str) -> dict:
    """Return complete donor info (including unmasked docs) for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None

    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found."
        )

    users_table = get_users_table()
    u_res = users_table.select("*").eq("id", donor["user_id"]).execute()
    user = u_res.data[0] if u_res.data else None

    organs_table = get_organ_registrations_table()
    o_res = organs_table.select("*").eq("donor_id", donor_id).execute()
    organs = []
    for o in o_res.data:
        organs.append({
            "registration_id": str(o["id"]),
            "organ_name": o.get("organ_name"),
            "blood_group": o.get("blood_group"),
            "health_report": o.get("health_report"),
            "hospitals_selected": o.get("hospitals_selected", []),
            "state": o.get("state", ""),
            "city": o.get("city", ""),
            "is_available": o.get("is_available", True),
        })

    return {
        "donor_id": donor_id,
        "user_id": donor["user_id"],
        "name": _safe_user_name(user),
        "email": user.get("email", "") if user else "",
        "age": donor.get("age"),
        "father_name": donor.get("father_name", ""),
        "contact_number": user.get("contact_number", "") if user else "",
        "state": donor.get("state", ""),
        "city": donor.get("city", ""),
        "full_address": donor.get("full_address", ""),
        "aadhaar_number": donor.get("aadhaar_number", "N/A"),
        "pan_number": donor.get("pan_number", "N/A"),
        "verified": donor.get("verified", False),
        "status": donor.get("status", "pending"),
        "rejection_reason": donor.get("rejection_reason"),
        "verified_by_hospital": donor.get("verified_by_hospital"),
        "aadhaar_card_url": get_signed_url("aadhaar", donor.get("aadhaar_card_path", "")),
        "pan_card_url": get_signed_url("pan", donor.get("pan_card_path", "")),
        "medical_report_url": get_signed_url("medical", donor.get("medical_report_path", "")),
        "organ_registrations": organs,
        "created_at": donor.get("created_at"),
    }


# ── Approve Donor ─────────────────────────────────────────────────

async def approve_donor(admin_user_id: str, donor_id: str, notes: str = None) -> dict:
    """Set donor.verified=True, donor.status='approved'."""
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital.get("name", "Hospital")

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")

    if donor.get("status") == DonorStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Donor is already approved.")

    now = datetime.now(timezone.utc).isoformat()
    update_data = {
        "verified": True,
        "status": DonorStatus.APPROVED,
        "verified_by_hospital": hospital_name,
        "verified_by_admin_id": admin_user_id,
        "rejection_reason": None,
        "updated_at": now,
    }
    # NOTE: approval_notes column intentionally omitted — not in DB schema

    donors_table.update(update_data).eq("id", donor_id).execute()

    # Try to increment hospital approval counter (may fail if column absent)
    try:
        hospitals_table = get_hospitals_table()
        hospitals_table.update({
            "total_approvals": (hospital.get("total_approvals") or 0) + 1,
            "updated_at": now
        }).eq("id", hospital["id"]).execute()
    except Exception:
        pass  # Non-critical

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
    """Set donor.verified=False, donor.status='rejected'."""
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital.get("name", "Hospital")

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")

    if donor.get("status") == DonorStatus.REJECTED:
        raise HTTPException(status_code=409, detail="Donor is already rejected.")

    now = datetime.now(timezone.utc).isoformat()
    donors_table.update({
        "verified": False,
        "status": DonorStatus.REJECTED,
        "rejection_reason": rejection_reason,
        "verified_by_hospital": hospital_name,
        "verified_by_admin_id": admin_user_id,
        "updated_at": now,
    }).eq("id", donor_id).execute()

    try:
        hospitals_table = get_hospitals_table()
        hospitals_table.update({
            "total_rejections": (hospital.get("total_rejections") or 0) + 1,
            "updated_at": now
        }).eq("id", hospital["id"]).execute()
    except Exception:
        pass  # Non-critical

    logger.info(f"Donor REJECTED: donor_id={donor_id} | hospital={hospital_name}")
    return {
        "donor_id": donor_id,
        "new_status": DonorStatus.REJECTED,
        "verified": False,
        "action_by_hospital": hospital_name,
        "message": "Donor registration has been rejected.",
    }


# ── Receiver Listing ──────────────────────────────────────────────

async def list_all_receivers(
    admin_user_id: str,
    page: int = 1,
    page_size: int = 10,
    status_filter: str = "all",
) -> dict:
    """Paginated receiver list for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    receivers_table = get_receivers_table()
    users_table = get_users_table()

    # status column may not exist — fetch all, then filter in Python if needed
    query = receivers_table.select("*")
    total_res = query.execute()
    all_receivers = total_res.data

    # Filter status in Python since column may be missing in DB
    if status_filter != "all":
        all_receivers = [r for r in all_receivers if r.get("status", "pending") == status_filter]

    total = len(all_receivers)
    skip = (page - 1) * page_size
    receivers = all_receivers[skip:skip + page_size]

    items = []
    for recv in receivers:
        u_res = users_table.select("*").eq("id", recv["user_id"]).execute()
        user = u_res.data[0] if u_res.data else None
        if not user:
            continue

        items.append({
            "receiver_id": str(recv["id"]),
            "user_id": recv["user_id"],
            "name": _safe_user_name(user),
            "email": user.get("email", ""),
            "contact_number": user.get("contact_number", ""),
            "age": recv.get("age"),
            "father_name": recv.get("father_name", ""),
            "state": recv.get("state", ""),
            "city": recv.get("city", ""),
            "status": recv.get("status", "pending"),
            "organ_name": recv.get("organ_name", "N/A"),
            "aadhaar_card_url": get_signed_url("aadhaar", recv.get("aadhaar_card_path", "")),
            "pan_card_url": get_signed_url("pan", recv.get("pan_card_path", "")),
            "medical_report_url": get_signed_url("medical", recv.get("medical_report_path", "")),
            "created_at": recv.get("created_at"),
        })

    return paginate_response(items, total, page, page_size)


# ── Receiver Verification ────────────────────────────────────────

async def approve_receiver(admin_user_id: str, receiver_id: str) -> dict:
    hospital = await _get_hospital_for_admin(admin_user_id)
    receivers_table = get_receivers_table()

    now = datetime.now(timezone.utc).isoformat()
    update_data = {"updated_at": now}

    # Add optional columns only if they exist (graceful degradation)
    try:
        receivers_table.update({
            **update_data,
            "status": "approved",
            "verified_by_hospital": hospital.get("name", ""),
            "verified_by_admin_id": admin_user_id,
        }).eq("id", receiver_id).execute()
    except Exception:
        # Fallback: update only what exists
        receivers_table.update(update_data).eq("id", receiver_id).execute()

    logger.info(f"Receiver APPROVED: {receiver_id} by {hospital.get('name')}")
    return {"message": "Receiver approved successfully.", "status": "approved"}


async def reject_receiver(admin_user_id: str, receiver_id: str) -> dict:
    hospital = await _get_hospital_for_admin(admin_user_id)
    receivers_table = get_receivers_table()

    now = datetime.now(timezone.utc).isoformat()
    try:
        receivers_table.update({
            "status": "rejected",
            "verified_by_hospital": hospital.get("name", ""),
            "verified_by_admin_id": admin_user_id,
            "updated_at": now,
        }).eq("id", receiver_id).execute()
    except Exception:
        receivers_table.update({"updated_at": now}).eq("id", receiver_id).execute()

    logger.info(f"Receiver REJECTED: {receiver_id} by {hospital.get('name')}")
    return {"message": "Receiver rejected.", "status": "rejected"}


# ── Admin's Hospital Profile ──────────────────────────────────────

async def get_hospital_profile(admin_user_id: str) -> dict:
    """Return the hospital profile for the logged-in admin."""
    hospital = await _get_hospital_for_admin(admin_user_id)
    return {
        "hospital_id": str(hospital["id"]),
        "name": hospital.get("name", ""),
        "state": hospital.get("state", ""),
        "city": hospital.get("city", ""),
        "registration_number": hospital.get("registration_number", ""),
        "total_approvals": hospital.get("total_approvals", 0),
        "total_rejections": hospital.get("total_rejections", 0),
        "created_at": hospital.get("created_at"),
    }

async def get_platform_stats(admin_user_id: str) -> dict:
    """Return administrative overview of the entire system."""
    await _get_hospital_for_admin(admin_user_id) # Auth check
    from app.services.match_service import get_global_stats
    return await get_global_stats()
