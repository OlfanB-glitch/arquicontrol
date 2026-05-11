from app.core.database import get_database
from app.modules.materiales.domain.repositories import IMaterialRepository


class MaterialRepository(IMaterialRepository):
    def __init__(self):
        self.collection = get_database().materiales

    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("nombre", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, material_id: str) -> dict | None:
        return await self.collection.find_one({"id": material_id}, {"_id": 0})

    async def get_by_code(self, code: str, user_id: str | None = None) -> dict | None:
        query = {"codigoMaterial": code}
        if user_id:
            query["userId"] = user_id
        return await self.collection.find_one(query, {"_id": 0})

    async def create(self, data: dict) -> dict:
        await self.collection.insert_one(dict(data))
        return data

    async def update(self, material_id: str, data: dict) -> dict | None:
        await self.collection.update_one({"id": material_id}, {"$set": data})
        return await self.get_by_id(material_id)
