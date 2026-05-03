from fastapi import HTTPException, status

from app.modules.contratistas.domain.models import (
    ContratistaCreate,
    ContratistaResponse,
    ContratistaUpdate,
)
from app.modules.contratistas.infrastructure.repository import ContratistaRepository
from app.shared.common import create_audit_fields, touch_updated_at


class ContratistaService:
    def __init__(self, repository: ContratistaRepository):
        self.repository = repository

    async def list_all(self) -> list[ContratistaResponse]:
        return [ContratistaResponse(**item) for item in await self.repository.list_all()]

    async def create(self, payload: ContratistaCreate) -> ContratistaResponse:
        existing = await self.repository.get_by_document(payload.numeroDocumento)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Documento ya registrado")
        contractor = {**payload.model_dump(), **create_audit_fields()}
        created = await self.repository.create(contractor)
        return ContratistaResponse(**created)

    async def update(self, contractor_id: str, payload: ContratistaUpdate) -> ContratistaResponse:
        current = await self.repository.get_by_id(contractor_id)
        if not current:
            raise HTTPException(status_code=404, detail="Contratista no encontrado")
        existing = await self.repository.get_by_document(payload.numeroDocumento)
        if existing and existing["id"] != contractor_id:
            raise HTTPException(status_code=409, detail="Documento ya registrado")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(contractor_id, updated)
        return ContratistaResponse(**saved)


contratista_service = ContratistaService(ContratistaRepository())