from fastapi import HTTPException, status

from app.modules.proveedores.domain.models import ProveedorCreate, ProveedorResponse, ProveedorUpdate
from app.modules.proveedores.infrastructure.repository import ProveedorRepository
from app.shared.common import create_audit_fields, touch_updated_at


class ProveedorService:
    def __init__(self, repository: ProveedorRepository):
        self.repository = repository

    async def list_all(self, user_id: str) -> list[ProveedorResponse]:
        return [ProveedorResponse(**item) for item in await self.repository.list_all(user_id)]

    async def create(self, payload: ProveedorCreate, user_id: str) -> ProveedorResponse:
        existing = await self.repository.get_by_nit(payload.nit, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIT ya registrado")
        data = {**payload.model_dump(), **create_audit_fields(), "userId": user_id}
        created = await self.repository.create(data)
        return ProveedorResponse(**created)

    async def update(self, proveedor_id: str, payload: ProveedorUpdate, user_id: str) -> ProveedorResponse:
        current = await self.repository.get_by_id(proveedor_id)
        if not current or current.get("userId") != user_id:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        duplicated = await self.repository.get_by_nit(payload.nit, user_id)
        if duplicated and duplicated["id"] != proveedor_id:
            raise HTTPException(status_code=409, detail="NIT ya registrado")
        updated = touch_updated_at({**current, **payload.model_dump()})
        saved = await self.repository.update(proveedor_id, updated)
        return ProveedorResponse(**saved)


proveedor_service = ProveedorService(ProveedorRepository())
