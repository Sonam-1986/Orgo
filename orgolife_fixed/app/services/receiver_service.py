"""
Receiver service — profile creation and donor search engine.
"""
import logging
from typing import Optional, List
from fastapi import HTTPException, UploadFile, status
from app.db.database import (
    get_users_table, get_receivers_table,
    get_donors_table, get_organ_registrations_table
)
from app.models.receiver import receiver_document
from app.models.user import UserRole
from app.schemas.receiver import ReceiverSignupStep1, DonorSearchRequest
from app.services.file_service import save_upload, get_signed_url
from app.utils.masking import mask_aadhaar
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


# ── Step 1: Receiver Registration ────────────────────────────────

async def register_receiver(
    user_id: str,
    data: ReceiverSignupStep1,
    aadhaar_file: UploadFile,
    pan_file: UploadFile,
    medical_file: UploadFile,
) -> dict:
    """Validate user and create receiver profile with uploaded documents."""
    users = get_users_table()
    user_res = users.select("*").eq("id", user_id).execute()
    user = user_res.data[0] if user_res.data else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if receiver profile already exists
    receivers = get_receivers_table()
    existing = receivers.select("id").eq("user_id", user_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Receiver profile already exists for this user."
        )

    users.update({"role": UserRole.RECEIVER}).eq("id", user_id).execute()

    aadhaar_path = await save_upload(aadhaar_file, "aadhaar", user_id, "aadhaar_card")
    pan_path = await save_upload(pan_file, "pan", user_id, "pan_card")
    medical_path = await save_upload(medical_file, "medical_reports", user_id, "medical_report")

    doc = receiver_document(
        user_id=user_id,
        age=data.age,
        father_name=data.father_name,
        state=data.state,
        city=data.city,
        aadhaar_card_path=aadhaar_path,
        pan_card_path=pan_path,
        medical_report_path=medical_path,
        organ_name=data.organ_name,
        aadhaar_number=data.aadhaar_number,
        pan_number=data.pan_number,
    )
    result = receivers.insert(doc).execute()

    logger.info(f"Receiver registered: user_id={user_id}")
    return {
        "user_id": user_id,
        "receiver_id": str(result.data[0]["id"]),
        "message": "Receiver registered successfully. You can now search for donors.",
    }


# ── Step 2: Donor Search ──────────────────────────────────────────

async def search_donors(req: DonorSearchRequest) -> dict:
    """
    Search organ_registrations with filters, JOIN user + donor data,
    return masked results with pagination.
    """
    organs_table = get_organ_registrations_table()
    donors_table = get_donors_table()
    users_table = get_users_table()

    try:
        # 1. Query organs with filters (Exact matching for location to prevent timeouts)
        col_list = "id, donor_id, user_id, organ_name, blood_group, state, city, hospitals_selected"
        query = organs_table.select(col_list).eq("organ_name", req.organ_type.value).eq("blood_group", req.blood_group.value).eq("is_available", True)

        if req.state:
            query = query.eq("state", req.state)
        if req.city:
            query = query.eq("city", req.city)

        skip = (req.page - 1) * req.page_size
        response = query.range(skip, skip + req.page_size - 1).execute()
        
        organs = response.data or []
        # Fallback count: local size + offset (not exact but prevents 1101 crashes on Supabase)
        total = len(organs) + skip if organs else 0

        if not organs:
            return paginate_response([], 0, req.page, req.page_size)

        # 2. Batch fetch donors (strictly validated UUIDs)
        uuid_pattern = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        import re
        donor_ids = [o["donor_id"] for o in organs if o.get("donor_id") and re.match(uuid_pattern, str(o["donor_id"]))]
        
        if not donor_ids:
            return paginate_response([], 0, req.page, req.page_size)
            
        donors_res = donors_table.select("*").in_("id", donor_ids).execute()
        donors_map = {d["id"]: d for d in (donors_res.data or [])}

        # 3. Batch fetch users
        user_ids = [d["user_id"] for d in donors_map.values() if d.get("user_id") and re.match(uuid_pattern, str(d["user_id"]))]
        users_map = {}
        if user_ids:
            users_res = users_table.select("*").in_("id", user_ids).execute()
            users_map = {u["id"]: u for u in (users_res.data or [])}

        # 4. Assemble results
        results = []
        for organ in organs:
            donor = donors_map.get(organ.get("donor_id"))
            if not donor:
                continue

            v_status = (donor.get("status") or "").lower()
            is_legal = donor.get("verified") and v_status == "approved"
            
            if req.verified_donor == "yes" and not is_legal:
                continue
            elif req.verified_donor == "no" and donor.get("verified"):
                continue

            if req.hospital_name:
                selected = [h.lower() for h in (organ.get("hospitals_selected") or [])]
                if not any(req.hospital_name.lower() in h for h in selected):
                    continue

            user = users_map.get(donor.get("user_id"))
            if not user:
                continue

            verification_status = "legal" if is_legal else ("illegal" if v_status == "rejected" else "pending")

            results.append({
                "donor_name": user.get("name", "Donor"),
                "age": donor.get("age", "N/A"),
                "father_name": donor.get("father_name", "N/A"),
                "aadhaar_number_masked": mask_aadhaar(donor.get("aadhaar_number", "")),
                "blood_group": organ.get("blood_group", "N/A"),
                "organ": organ.get("organ_name", "N/A"),
                "hospital_verified_by": donor.get("verified_by_hospital", "Awaiting"),
                "verification_status": verification_status,
                "contact_number": user.get("contact_number", "N/A"),
                "state": organ.get("state", ""),
                "city": organ.get("city", ""),
                "full_address": donor.get("full_address", "N/A"),
                "aadhaar_card_url": get_signed_url("aadhaar", donor.get("aadhaar_card_path", "")),
                "pan_card_url": get_signed_url("pan", donor.get("pan_card_path", "")),
                "medical_report_url": get_signed_url("medical", donor.get("medical_report_path", "")),
            })

        return paginate_response(results, total, req.page, req.page_size)
    except Exception as e:
        logger.error(f"STRICT SEARCH FAILURE: {e}", exc_info=True)
        # Strip HTML to avoid messy UI if Supabase returns a Cloudflare error page
        err_msg = str(e)
        if "<html" in err_msg.lower():
            err_msg = "Database timeout/connection error (Supabase). Please try again in a moment."
        raise HTTPException(
            status_code=500, 
            detail=f"Permanent Fix Search Error: {err_msg}. Please make sure to REFRESH your browser page entirely."
        )


# ── Receiver profile ──────────────────────────────────────────────

async def get_receiver_profile(user_id: str) -> dict:
    receivers = get_receivers_table()
    res = receivers.select("*").eq("user_id", user_id).execute()
    receiver = res.data[0] if res.data else None
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver profile not found.")

    users = get_users_table()
    u_res = users.select("*").eq("id", user_id).execute()
    user = u_res.data[0] if u_res.data else None

    name = ""
    contact_number = ""
    email = ""
    if user:
        name = user.get("name") or user.get("full_name", "")
        email = user.get("email", "")
        contact_number = user.get("contact_number", "")

    return {
        "receiver_id": str(receiver["id"]),
        "user_id": user_id,
        "name": name,
        "email": email,
        "age": receiver.get("age"),
        "father_name": receiver.get("father_name", ""),
        "organ_name": receiver.get("organ_name", ""),
        "contact_number": contact_number,
        "state": receiver.get("state", ""),
        "city": receiver.get("city", ""),
        "status": receiver.get("status", "pending"),
        "created_at": receiver.get("created_at"),
    }
