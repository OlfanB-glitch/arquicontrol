from fastapi import APIRouter, Depends

from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
from app.modules.materiales.application.service import material_service
from app.modules.materiales.domain.models import MaterialCreate, MaterialResponse, MaterialUpdate


router = APIRouter(prefix="/materiales", tags=["materiales"])


@router.get("", response_model=list[MaterialResponse])
async def list_materiales(_: UserResponse = Depends(get_current_user)):
    return await material_service.list_all()


@router.post("", response_model=MaterialResponse)
async def create_material(
    payload: MaterialCreate,
    _: UserResponse = Depends(get_current_user),
):
    return await material_service.create(payload)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: str,
    payload: MaterialUpdate,
    _: UserResponse = Depends(get_current_user),
):
    return await material_service.update(material_id, payload)