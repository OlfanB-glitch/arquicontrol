from app.core.database import get_database
from app.modules.clientes.domain.repositories import IClienteRepository


class ClienteRepository(IClienteRepository):
    def __init__(self):
        self.collection = get_database().clientes

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("nombreCompleto", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, client_id: str) -> dict | None:
        return await self.collection.find_one({"id": client_id}, {"_id": 0})

    async def get_by_document(self, document_number: str) -> dict | None:
        return await self.collection.find_one(
            {"numeroDocumento": document_number},
            {"_id": 0},
        )

    async def create(self, client_data: dict) -> dict:
        await self.collection.insert_one(dict(client_data))
        return client_data

    async def update(self, client_id: str, client_data: dict) -> dict | None:
        await self.collection.update_one({"id": client_id}, {"$set": client_data})
        return await self.get_by_id(client_id)