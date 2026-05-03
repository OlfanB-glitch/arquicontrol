from app.core.database import get_database
from app.modules.proveedores.domain.repositories import IProveedorRepository


class ProveedorRepository(IProveedorRepository):
    def __init__(self):
        self.collection = get_database().proveedores

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("nombre", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, proveedor_id: str) -> dict | None:
        return await self.collection.find_one({"id": proveedor_id}, {"_id": 0})

    async def get_by_nit(self, nit: str) -> dict | None:
        return await self.collection.find_one({"nit": nit}, {"_id": 0})

    async def create(self, proveedor_data: dict) -> dict:
        await self.collection.insert_one(dict(proveedor_data))
        return proveedor_data

    async def update(self, proveedor_id: str, proveedor_data: dict) -> dict | None:
        await self.collection.update_one({"id": proveedor_id}, {"$set": proveedor_data})
        return await self.get_by_id(proveedor_id)