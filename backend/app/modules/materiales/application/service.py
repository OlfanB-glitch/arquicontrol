from fastapi import HTTPException, status

from app.modules.materiales.domain.models import MaterialCreate, MaterialResponse, MaterialUpdate
from app.modules.materiales.infrastructure.repository import MaterialRepository
from app.shared.common import create_audit_fields, touch_updated_at


class MaterialService:
    def __init__(self, repository: MaterialRepository):
        self.repository = repository

    async def list_all(self) -> list[MaterialResponse]:
        return [MaterialResponse(**item) for item in await self.repository.list_all()]

    async def create(self, payload: MaterialCreate) -> MaterialResponse:
        existing = await self.repository.get_by_code(payload.codigoMaterial)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de material ya registrado")
        material = {**payload.model_dump(), **create_audit_fields()}
        created = await self.repository.create(material)
        return MaterialResponse(**created)

    async def update(self, material_id: str, payload: MaterialUpdate) -> MaterialResponse:
        current = await self.repository.get_by_id(material_id)
        if not current:
            raise HTTPException(status_code=404, detail="Material no encontrado")
        existing = await self.repository.get_by_code(payload.codigoMaterial)
        if existing and existing["id"] != material_id:
            raise HTTPException(status_code=409, detail="Código de material ya registrado")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(material_id, updated)
        return MaterialResponse(**saved)


material_service = MaterialService(MaterialRepository())