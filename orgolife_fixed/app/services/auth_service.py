"""
Auth service — register users, login, refresh tokens.
Orchestrates DB access, password hashing, and JWT generation.
"""
import logging
from datetime import timedelta
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.database import get_users_collection, get_hospitals_collection
from app.models.user import UserRole, UserStatus, user_document
from app.models.hospital import hospital_document
from app.schemas.auth import LoginRequest, TokenResponse, AdminLoginRequest
from app.schemas.admin import HospitalAdminSignup
from app.utils.password import hash_password, verify_password
from app.utils.jwt_handler import (
    create_access_token, create_refresh_token,
    verify_refresh_token
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_token_response(user: dict) -> TokenResponse:
    """Build a TokenResponse from a DB user document."""
    user_id = str(user["_id"])
    token_data = {
        "sub": user_id,
        "role": user["role"],
        "email": user["email"],
        "name": user["name"],
    }
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user["role"],
        user_id=user_id,
        name=user["name"],
    )


# ── Donor / Receiver Registration ────────────────────────────────

async def register_user_step1(
    name: str,
    email: str,
    password: str,
    contact_number: str,
    role: UserRole,
) -> dict:
    """
    Create a user account (common step for donor & receiver).
    Returns the inserted user document's _id as string.
    """
    users = get_users_collection()

    # Duplicate email check
    existing = await users.find_one({"email": email.lower().strip()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    doc = user_document(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        contact_number=contact_number,
    )
    result = await users.insert_one(doc)
    logger.info(f"New user registered: {email} | role: {role}")
    return {"user_id": str(result.inserted_id)}


# ── Hospital Admin Registration ───────────────────────────────────

async def register_hospital_admin(payload: HospitalAdminSignup) -> dict:
    """Register a hospital admin + create the hospital record atomically."""
    users = get_users_collection()
    hospitals = get_hospitals_collection()

    # Email uniqueness
    if await users.find_one({"email": payload.email.lower().strip()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An admin account with this email already exists."
        )

    # Hospital registration number uniqueness
    if await hospitals.find_one(
        {"registration_number": payload.hospital_registration_number}
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this registration number already exists."
        )

    # Insert user
    user_doc = user_document(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.HOSPITAL_ADMIN,
        contact_number=payload.contact_number,
    )
    user_result = await users.insert_one(user_doc)
    admin_user_id = str(user_result.inserted_id)

    # Insert hospital
    hosp_doc = hospital_document(
        name=payload.hospital_name,
        admin_user_id=admin_user_id,
        state=payload.hospital_state,
        city=payload.hospital_city,
        address=payload.hospital_address,
        contact_number=payload.hospital_contact,
        registration_number=payload.hospital_registration_number,
    )
    hosp_result = await hospitals.insert_one(hosp_doc)

    logger.info(f"Hospital admin registered: {payload.email} | hospital: {payload.hospital_name}")
    return {
        "user_id": admin_user_id,
        "hospital_id": str(hosp_result.inserted_id),
    }


# ── Login ─────────────────────────────────────────────────────────

async def login_user(payload: LoginRequest, expected_role: UserRole) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    users = get_users_collection()
    user = await users.find_one({"email": payload.email.lower().strip()})

    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user["role"] != expected_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This login endpoint is for '{expected_role}' accounts only."
        )

    if user.get("status") not in ("active", UserStatus.ACTIVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended. Contact support.",
        )

    logger.info(f"Login successful: {payload.email}")
    return _build_token_response(user)


async def login_admin(payload: AdminLoginRequest) -> TokenResponse:
    """Admin login — also validates hospital code (registration number)."""
    users = get_users_collection()
    hospitals = get_hospitals_collection()

    user = await users.find_one({"email": payload.email.lower().strip()})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user["role"] != UserRole.HOSPITAL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for Hospital Admins only."
        )

    # Validate hospital_code
    hospital = await hospitals.find_one({
        "admin_user_id": str(user["_id"]),
        "registration_number": payload.hospital_code,
    })
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid hospital code. Access denied."
        )

    logger.info(f"Admin login: {payload.email}")
    return _build_token_response(user)


# ── Token Refresh ─────────────────────────────────────────────────

async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Issue a new access token using a valid refresh token."""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    users = get_users_collection()
    user = await users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return _build_token_response(user)
