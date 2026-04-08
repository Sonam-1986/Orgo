"""
Receiver routes:
  POST /receivers/register   — Step 1: receiver onboarding (multipart)
  POST /receivers/search     — search verified donors
  GET  /receivers/profile    — own profile
"""
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from typing import Optional

from app.core.dependencies import require_receiver
from app.schemas.receiver import ReceiverSignupStep1, DonorSearchRequest
from app.schemas.common import BaseResponse
from app.services import receiver_service

router = APIRouter(prefix="/receivers", tags=["Receivers"])


@router.post(
    "/register",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Receiver (multipart/form-data)",
)
async def register_receiver(
    name: str = Form(...),
    age: int = Form(...),
    father_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    contact_number: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    aadhaar_file: UploadFile = File(...),
    pan_file: UploadFile = File(...),
    medical_file: UploadFile = File(...),
):
    data = ReceiverSignupStep1(
        name=name, age=age, father_name=father_name,
        email=email, password=password, contact_number=contact_number,
        state=state, city=city,
        aadhaar_number=aadhaar_number, pan_number=pan_number,
    )
    result = await receiver_service.register_receiver(data, aadhaar_file, pan_file, medical_file)
    return BaseResponse(message=result["message"], data=result)


@router.post(
    "/search",
    response_model=BaseResponse,
    summary="Search Donors",
)
async def search_donors(
    payload: DonorSearchRequest,
    current_user: dict = Depends(require_receiver),
):
    result = await receiver_service.search_donors(payload)
    return BaseResponse(data=result)


@router.get(
    "/profile",
    response_model=BaseResponse,
    summary="Get Receiver Profile",
)
async def get_profile(current_user: dict = Depends(require_receiver)):
    profile = await receiver_service.get_receiver_profile(current_user["sub"])
    return BaseResponse(data=profile)
