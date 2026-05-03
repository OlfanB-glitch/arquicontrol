from fastapi import HTTPException, status

from app.modules.clientes.domain.models import ClienteCreate, ClienteResponse, ClienteUpdate
from app.modules.clientes.infrastructure.repository import ClienteRepository
from app.shared.common import create_audit_fields, touch_updated_at


class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository

    async def list_all(self) -> list[ClienteResponse]:
        return [ClienteResponse(**item) for item in await self.repository.list_all()]

    async def create(self, payload: ClienteCreate) -> ClienteResponse:
        existing_client = await self.repository.get_by_document(payload.numeroDocumento)
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese documento",
            )

        client_data = {**payload.model_dump(), **create_audit_fields()}
        created = await self.repository.create(client_data)
        return ClienteResponse(**created)

    async def update(self, client_id: str, payload: ClienteUpdate) -> ClienteResponse:
        current = await self.repository.get_by_id(client_id)
        if not current:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        duplicated = await self.repository.get_by_document(payload.numeroDocumento)
        if duplicated and duplicated["id"] != client_id:
            raise HTTPException(status_code=409, detail="Documento ya registrado")

        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(client_id, updated)
        return ClienteResponse(**saved)


cliente_service = ClienteService(ClienteRepository())