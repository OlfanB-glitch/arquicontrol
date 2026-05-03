from app.core.database import get_database
from app.modules.contratistas.domain.repositories import IContratistaRepository


class ContratistaRepository(IContratistaRepository):
    def __init__(self):
        self.collection = get_database().contratistas

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("nombreCompleto", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, contractor_id: str) -> dict | None:
        return await self.collection.find_one({"id": contractor_id}, {"_id": 0})

    async def get_by_document(self, document_number: str) -> dict | None:
        return await self.collection.find_one({"numeroDocumento": document_number}, {"_id": 0})

    async def create(self, contractor_data: dict) -> dict:
        await self.collection.insert_one(dict(contractor_data))
        return contractor_data

    async def update(self, contractor_id: str, contractor_data: dict) -> dict | None:
        await self.collection.update_one({"id": contractor_id}, {"$set": contractor_data})
        return await self.get_by_id(contractor_id)