from fastapi import HTTPException, status

from app.modules.contratistas.domain.models import ContratistaCreate, ContratistaResponse, ContratistaUpdate
from app.modules.contratistas.infrastructure.repository import ContratistaRepository
from app.shared.common import create_audit_fields, touch_updated_at


class ContratistaService:
    def __init__(self, repository: ContratistaRepository):
        self.repository = repository

    async def list_all(self, user_id: str) -> list[ContratistaResponse]:
        return [ContratistaResponse(**item) for item in await self.repository.list_all(user_id)]

    async def create(self, payload: ContratistaCreate, user_id: str) -> ContratistaResponse:
        existing = await self.repository.get_by_document(payload.numeroDocumento, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contratista ya registrado con ese documento")
        data = {**payload.model_dump(), **create_audit_fields(), "userId": user_id}
        created = await self.repository.create(data)
        return ContratistaResponse(**created)

    async def update(self, contractor_id: str, payload: ContratistaUpdate, user_id: str) -> ContratistaResponse:
        current = await self.repository.get_by_id(contractor_id)
        if not current or current.get("userId") != user_id:
            raise HTTPException(status_code=404, detail="Contratista no encontrado")
        duplicated = await self.repository.get_by_document(payload.numeroDocumento, user_id)
        if duplicated and duplicated["id"] != contractor_id:
            raise HTTPException(status_code=409, detail="Contratista ya registrado con ese documento")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(contractor_id, updated)
        return ContratistaResponse(**saved)


contratista_service = ContratistaService(ContratistaRepository())
