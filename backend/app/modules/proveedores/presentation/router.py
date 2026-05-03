from fastapi import APIRouter, Depends

from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
from app.modules.proveedores.application.service import proveedor_service
from app.modules.proveedores.domain.models import ProveedorCreate, ProveedorResponse, ProveedorUpdate


router = APIRouter(prefix="/proveedores", tags=["proveedores"])


@router.get("", response_model=list[ProveedorResponse])
async def list_proveedores(_: UserResponse = Depends(get_current_user)):
    return await proveedor_service.list_all()


@router.post("", response_model=ProveedorResponse)
async def create_proveedor(
    payload: ProveedorCreate,
    _: UserResponse = Depends(get_current_user),
):
    return await proveedor_service.create(payload)


@router.put("/{proveedor_id}", response_model=ProveedorResponse)
async def update_proveedor(
    proveedor_id: str,
    payload: ProveedorUpdate,
    _: UserResponse = Depends(get_current_user),
):
    return await proveedor_service.update(proveedor_id, payload)