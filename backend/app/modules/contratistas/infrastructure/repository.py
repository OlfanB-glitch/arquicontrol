from app.core.database import get_database
from app.modules.contratistas.domain.repositories import IContratistaRepository


class ContratistaRepository(IContratistaRepository):
    def __init__(self):
        self.collection = get_database().contratistas

    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("nombreCompleto", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, contractor_id: str) -> dict | None:
        return await self.collection.find_one({"id": contractor_id}, {"_id": 0})

    async def get_by_document(self, document_number: str, user_id: str) -> dict | None:
        return await self.collection.find_one(
            {"numeroDocumento": document_number, "userId": user_id}, {"_id": 0},
        )

    async def create(self, data: dict) -> dict:
        await self.collection.insert_one(dict(data))
        return data

    async def update(self, contractor_id: str, data: dict) -> dict | None:
        await self.collection.update_one({"id": contractor_id}, {"$set": data})
        return await self.get_by_id(contractor_id)
