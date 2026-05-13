from app.core.database import get_database
from app.modules.clientes.domain.repositories import IClienteRepository


class ClienteRepository(IClienteRepository):
    def __init__(self):
        self.collection = get_database().clientes

    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("nombreCompleto", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, client_id: str) -> dict | None:
        return await self.collection.find_one({"id": client_id}, {"_id": 0})

    async def get_by_document(self, document_number: str, user_id: str) -> dict | None:
        return await self.collection.find_one(
            {"numeroDocumento": document_number, "userId": user_id}, {"_id": 0},
        )

    async def create(self, data: dict) -> dict:
        await self.collection.insert_one(dict(data))
        return data

    async def update(self, client_id: str, data: dict) -> dict | None:
        await self.collection.update_one({"id": client_id}, {"$set": data})
        return await self.get_by_id(client_id)

    async def aggregate_stats(self, user_id: str) -> dict:
        """
        Pipeline de estadísticas de clientes usando:
          $addFields — calcula si el cliente tiene observaciones
          $facet     — múltiples sub-pipelines en paralelo
          $count     — cuenta clientes por estado
        """
        pipeline = [
            {"$match": {"userId": user_id}},

            # $addFields: agrega campos calculados sin modificar la colección
            {"$addFields": {
                "tieneObservaciones": {
                    "$and": [
                        {"$ne": ["$observaciones", None]},
                        {"$ne": ["$observaciones", ""]},
                    ]
                },
                "ciudadNormalizada": {"$toLower": "$ciudad"},
            }},

            # $facet: ejecuta sub-pipelines en paralelo
            {"$facet": {

                # Sub-pipeline A: $count por estado
                "porEstado": [
                    {"$group": {
                        "_id": "$estado",
                        "total": {"$sum": 1},
                    }},
                ],

                # Sub-pipeline B: $count por ciudad
                "porCiudad": [
                    {"$group": {
                        "_id": "$ciudadNormalizada",
                        "total": {"$sum": 1},
                    }},
                    {"$sort": {"total": -1}},
                    {"$limit": 5},
                ],

                # Sub-pipeline C: total de clientes
                "totales": [
                    {"$count": "totalClientes"},
                ],

                # Sub-pipeline D: clientes con observaciones
                "conObservaciones": [
                    {"$match": {"tieneObservaciones": True}},
                    {"$count": "cantidad"},
                ],
            }},
        ]
        results = await self.collection.aggregate(pipeline).to_list(1)
        return results[0] if results else {}