from fastapi import HTTPException, status

from app.modules.clientes.domain.models import ClienteCreate, ClienteResponse, ClienteUpdate
from app.modules.clientes.infrastructure.repository import ClienteRepository
from app.shared.common import create_audit_fields, touch_updated_at


class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository

    async def list_all(self, user_id: str) -> list[ClienteResponse]:
        return [ClienteResponse(**item) for item in await self.repository.list_all(user_id)]

    async def create(self, payload: ClienteCreate, user_id: str) -> ClienteResponse:
        existing = await self.repository.get_by_document(payload.numeroDocumento, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente ya registrado con ese documento")
        data = {**payload.model_dump(), **create_audit_fields(), "userId": user_id}
        created = await self.repository.create(data)
        return ClienteResponse(**created)

    async def update(self, client_id: str, payload: ClienteUpdate, user_id: str) -> ClienteResponse:
        current = await self.repository.get_by_id(client_id)
        if not current or current.get("userId") != user_id:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        duplicated = await self.repository.get_by_document(payload.numeroDocumento, user_id)
        if duplicated and duplicated["id"] != client_id:
            raise HTTPException(status_code=409, detail="Cliente ya registrado con ese documento")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(client_id, updated)
        return ClienteResponse(**saved)


cliente_service = ClienteService(ClienteRepository())
