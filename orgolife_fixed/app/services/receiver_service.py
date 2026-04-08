"""
Receiver service — profile creation and donor search engine.
"""
import logging
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException, UploadFile

from app.db.database import (
    get_users_collection, get_receivers_collection,
    get_donors_collection, get_organ_registrations_collection
)
from app.models.receiver import receiver_document
from app.models.user import UserRole
from app.schemas.receiver import ReceiverSignupStep1, DonorSearchRequest
from app.services.auth_service import register_user_step1
from app.services.file_service import save_upload
from app.utils.masking import mask_aadhaar
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


# ── Step 1: Receiver Registration ────────────────────────────────

async def register_receiver(
    data: ReceiverSignupStep1,
    aadhaar_file: UploadFile,
    pan_file: UploadFile,
    medical_file: UploadFile,
) -> dict:
    """Create user account + receiver profile with uploaded documents."""
    user_result = await register_user_step1(
        name=data.name,
        email=data.email,
        password=data.password,
        contact_number=data.contact_number,
        role=UserRole.RECEIVER,
    )
    user_id = user_result["user_id"]

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
        aadhaar_number=data.aadhaar_number,
        pan_number=data.pan_number,
    )
    receivers = get_receivers_collection()
    result = await receivers.insert_one(doc)

    logger.info(f"Receiver registered: user_id={user_id}")
    return {
        "user_id": user_id,
        "receiver_id": str(result.inserted_id),
        "message": "Receiver registered successfully. You can now search for donors.",
    }


# ── Step 2: Donor Search ──────────────────────────────────────────

async def search_donors(req: DonorSearchRequest) -> dict:
    """
    Search organ_registrations with filters, JOIN user + donor data,
    return masked results with pagination.
    """
    organs_col = get_organ_registrations_collection()
    donors_col = get_donors_collection()
    users_col = get_users_collection()

    # ── Build organ query ─────────────────────────────────────────
    organ_query: dict = {
        "organ_name": req.organ_type,
        "blood_group": req.blood_group,
        "is_available": True,
    }
    if req.state:
        organ_query["state"] = {"$regex": req.state, "$options": "i"}
    if req.city:
        organ_query["city"] = {"$regex": req.city, "$options": "i"}

    # ── Build donor verification filter ──────────────────────────
    donor_filter: dict = {}
    if req.verified_donor == "yes":
        donor_filter["verified"] = True
        donor_filter["status"] = "approved"
    elif req.verified_donor == "no":
        donor_filter["verified"] = False

    # ── Fetch matching organ registrations ────────────────────────
    skip = (req.page - 1) * req.page_size
    total = await organs_col.count_documents(organ_query)
    cursor = organs_col.find(organ_query).skip(skip).limit(req.page_size)

    results = []
    async for organ in cursor:
        donor_id = organ.get("donor_id")
        if not donor_id:
            continue

        # Fetch donor profile
        donor = await donors_col.find_one({"_id": ObjectId(donor_id), **donor_filter})
        if not donor:
            continue

        # Hospital name filter (applied post-join)
        if req.hospital_name:
            selected = [h.lower() for h in organ.get("hospitals_selected", [])]
            if not any(req.hospital_name.lower() in h for h in selected):
                continue

        # Fetch user (name, contact)
        user = await users_col.find_one({"_id": ObjectId(donor["user_id"])})
        if not user:
            continue

        # Determine verification status label
        if donor["verified"] and donor["status"] == "approved":
            verification_status = "legal"
        elif donor["status"] == "rejected":
            verification_status = "illegal"
        else:
            verification_status = "pending"

        results.append({
            "donor_name": user["name"],
            "father_name": donor["father_name"],
            "aadhaar_number_masked": mask_aadhaar(donor.get("aadhaar_number", "")),
            "blood_group": organ["blood_group"],
            "organ": organ["organ_name"],
            "hospital_verified_by": donor.get("verified_by_hospital"),
            "verification_status": verification_status,
            "contact_number": user["contact_number"],
            "state": donor["address"]["state"],
            "city": donor["address"]["city"],
            "full_address": donor["address"]["full_address"],
        })

    return paginate_response(results, total, req.page, req.page_size)


# ── Receiver profile ──────────────────────────────────────────────

async def get_receiver_profile(user_id: str) -> dict:
    receivers = get_receivers_collection()
    receiver = await receivers.find_one({"user_id": user_id})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver profile not found.")

    users = get_users_collection()
    user = await users.find_one({"_id": ObjectId(user_id)})

    return {
        "receiver_id": str(receiver["_id"]),
        "user_id": user_id,
        "name": user["name"],
        "email": user["email"],
        "age": receiver["age"],
        "father_name": receiver["father_name"],
        "contact_number": user["contact_number"],
        "state": receiver["location"]["state"],
        "city": receiver["location"]["city"],
        "created_at": receiver["created_at"].isoformat(),
    }
