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

    async def aggregate_stats(self, user_id: str) -> dict:
        """
        Pipeline de estadísticas de contratistas usando:
          $addFields — enriquece con campo de rango de tarifa
          $bucket    — agrupa por rango de tarifa base
          $facet     — múltiples sub-pipelines en paralelo
        """
        pipeline = [
            {"$match": {"userId": user_id}},

            # $addFields: clasifica al contratista según su tarifa
            {"$addFields": {
                "categoríaTarifa": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$tarifaBase", 1_000_000]}, "then": "Básica"},
                            {"case": {"$lt": ["$tarifaBase", 3_000_000]}, "then": "Media"},
                            {"case": {"$lt": ["$tarifaBase", 6_000_000]}, "then": "Alta"},
                        ],
                        "default": "Premium",
                    }
                },
                "especialidadNormalizada": {"$toLower": "$especialidad"},
            }},

            # $facet: múltiples análisis en paralelo
            {"$facet": {

                # Sub-pipeline A: $bucket por rango de tarifa
                "distribucionTarifas": [
                    {"$bucket": {
                        "groupBy": "$tarifaBase",
                        "boundaries": [0, 1_000_000, 3_000_000, 6_000_000, 10_000_000],
                        "default": "Más de 10M",
                        "output": {
                            "cantidad": {"$sum": 1},
                            "tarifaPromedio": {"$avg": "$tarifaBase"},
                        },
                    }},
                ],

                # Sub-pipeline B: por especialidad
                "porEspecialidad": [
                    {"$group": {
                        "_id": "$especialidad",
                        "total": {"$sum": 1},
                        "tarifaPromedio": {"$avg": "$tarifaBase"},
                    }},
                    {"$sort": {"total": -1}},
                ],

                # Sub-pipeline C: por estado usando $count
                "porEstado": [
                    {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
                ],

                # Sub-pipeline D: total general
                "totales": [
                    {"$count": "totalContratistas"},
                ],
            }},
        ]
        results = await self.collection.aggregate(pipeline).to_list(1)
        return results[0] if results else {}