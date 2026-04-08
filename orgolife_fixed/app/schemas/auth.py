"""
Auth schemas — Login, Register, Token responses.
"""
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


# ── Request schemas ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "donor@example.com",
                "password": "SecurePass123!"
            }
        }


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    hospital_code: str = Field(..., min_length=4, description="Unique hospital registration code")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Response schemas ─────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds
    role: UserRole
    user_id: str
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGci...",
                "refresh_token": "eyJhbGci...",
                "token_type": "bearer",
                "expires_in": 3600,
                "role": "donor",
                "user_id": "64abc...",
                "name": "Rajesh Kumar"
            }
        }


class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: UserRole
    contact_number: str
    created_at: str
