from app.core.database import get_database
from app.modules.materiales.domain.repositories import IMaterialRepository


class MaterialRepository(IMaterialRepository):
    def __init__(self):
        self.collection = get_database().materiales

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("nombre", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, material_id: str) -> dict | None:
        return await self.collection.find_one({"id": material_id}, {"_id": 0})

    async def get_by_code(self, code: str) -> dict | None:
        return await self.collection.find_one({"codigoMaterial": code}, {"_id": 0})

    async def create(self, material_data: dict) -> dict:
        await self.collection.insert_one(dict(material_data))
        return material_data

    async def update(self, material_id: str, material_data: dict) -> dict | None:
        await self.collection.update_one({"id": material_id}, {"$set": material_data})
        return await self.get_by_id(material_id)