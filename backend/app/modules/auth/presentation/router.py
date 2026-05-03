from fastapi import APIRouter, Depends

from app.modules.auth.application.service import auth_service, get_current_user
from app.modules.auth.domain.models import AuthResponse, LoginRequest, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    return await auth_service.login(payload)


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user