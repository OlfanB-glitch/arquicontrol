from fastapi import APIRouter, Depends

from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
from app.modules.contratistas.application.service import contratista_service
from app.modules.contratistas.domain.models import (
    ContratistaCreate,
    ContratistaResponse,
    ContratistaUpdate,
)


router = APIRouter(prefix="/contratistas", tags=["contratistas"])


@router.get("", response_model=list[ContratistaResponse])
async def list_contratistas(_: UserResponse = Depends(get_current_user)):
    return await contratista_service.list_all()


@router.post("", response_model=ContratistaResponse)
async def create_contratista(
    payload: ContratistaCreate,
    _: UserResponse = Depends(get_current_user),
):
    return await contratista_service.create(payload)


@router.put("/{contratista_id}", response_model=ContratistaResponse)
async def update_contratista(
    contratista_id: str,
    payload: ContratistaUpdate,
    _: UserResponse = Depends(get_current_user),
):
    return await contratista_service.update(contratista_id, payload)