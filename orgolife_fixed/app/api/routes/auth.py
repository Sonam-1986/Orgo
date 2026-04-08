"""
Auth routes:
  POST /auth/register/admin   — register hospital admin
  POST /auth/login            — donor / receiver login
  POST /auth/login/admin      — hospital admin login
  POST /auth/refresh          — refresh access token
  GET  /auth/me               — current user profile
"""
from fastapi import APIRouter, Depends, status
from app.schemas.auth import LoginRequest, AdminLoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.admin import HospitalAdminSignup
from app.schemas.common import BaseResponse
from app.services import auth_service
from app.core.dependencies import get_current_user
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/admin",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Hospital Admin",
)
async def register_admin(payload: HospitalAdminSignup):
    result = await auth_service.register_hospital_admin(payload)
    return BaseResponse(
        message="Hospital admin registered successfully.",
        data=result,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Donor / Receiver Login",
)
async def login(payload: LoginRequest, role: str = "donor"):
    """Login for donor or receiver. Pass ?role=receiver to switch."""
    expected = UserRole.RECEIVER if role == "receiver" else UserRole.DONOR
    return await auth_service.login_user(payload, expected)


@router.post(
    "/login/donor",
    response_model=TokenResponse,
    summary="Donor Login",
)
async def login_donor(payload: LoginRequest):
    return await auth_service.login_user(payload, UserRole.DONOR)


@router.post(
    "/login/receiver",
    response_model=TokenResponse,
    summary="Receiver Login",
)
async def login_receiver(payload: LoginRequest):
    return await auth_service.login_user(payload, UserRole.RECEIVER)


@router.post(
    "/login/admin",
    response_model=TokenResponse,
    summary="Hospital Admin Login",
)
async def login_admin(payload: AdminLoginRequest):
    return await auth_service.login_admin(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
)
async def refresh_token(payload: RefreshTokenRequest):
    return await auth_service.refresh_access_token(payload.refresh_token)


@router.get(
    "/me",
    response_model=BaseResponse,
    summary="Current User Info",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    return BaseResponse(data=current_user)
