from fastapi import APIRouter, Depends

from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
from app.modules.clientes.application.service import cliente_service
from app.modules.clientes.domain.models import ClienteCreate, ClienteResponse, ClienteUpdate


router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
async def list_clientes(current_user: UserResponse = Depends(get_current_user)):
    return await cliente_service.list_all(current_user.id)


@router.post("", response_model=ClienteResponse)
async def create_cliente(
    payload: ClienteCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await cliente_service.create(payload, current_user.id)


@router.put("/{client_id}", response_model=ClienteResponse)
async def update_cliente(
    client_id: str,
    payload: ClienteUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await cliente_service.update(client_id, payload, current_user.id)
