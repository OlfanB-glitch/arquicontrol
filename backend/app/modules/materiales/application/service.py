from fastapi import HTTPException, status

from app.modules.materiales.domain.models import MaterialCreate, MaterialResponse, MaterialUpdate
from app.modules.materiales.infrastructure.repository import MaterialRepository
from app.shared.common import create_audit_fields, touch_updated_at


class MaterialService:
    def __init__(self, repository: MaterialRepository):
        self.repository = repository

    async def list_all(self, user_id: str) -> list[MaterialResponse]:
        return [MaterialResponse(**item) for item in await self.repository.list_all(user_id)]

    async def create(self, payload: MaterialCreate, user_id: str) -> MaterialResponse:
        existing = await self.repository.get_by_code(payload.codigoMaterial, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de material ya registrado")
        data = {**payload.model_dump(), **create_audit_fields(), "userId": user_id}
        created = await self.repository.create(data)
        return MaterialResponse(**created)

    async def update(self, material_id: str, payload: MaterialUpdate, user_id: str) -> MaterialResponse:
        current = await self.repository.get_by_id(material_id)
        if not current or current.get("userId") != user_id:
            raise HTTPException(status_code=404, detail="Material no encontrado")
        duplicated = await self.repository.get_by_code(payload.codigoMaterial, user_id)
        if duplicated and duplicated["id"] != material_id:
            raise HTTPException(status_code=409, detail="Código de material ya registrado")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(material_id, updated)
        return MaterialResponse(**saved)


material_service = MaterialService(MaterialRepository())
