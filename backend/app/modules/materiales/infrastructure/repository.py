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

    async def aggregate_stats(self, user_id: str) -> dict:
        """
        Pipeline de estadísticas de materiales usando:
          $addFields — clasifica material por precio
          $bucket    — distribuye por rango de precio de referencia
          $facet     — múltiples sub-pipelines en paralelo
        """
        pipeline = [
            {"$match": {"userId": user_id}},

            # $addFields: clasifica el material según su precio
            {"$addFields": {
                "categoríaPrecio": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$precioReferencia", 50_000]}, "then": "Económico"},
                            {"case": {"$lt": ["$precioReferencia", 200_000]}, "then": "Medio"},
                            {"case": {"$lt": ["$precioReferencia", 500_000]}, "then": "Alto"},
                        ],
                        "default": "Premium",
                    }
                },
                "unidadNormalizada": {"$toLower": "$unidadMedida"},
            }},

            # $facet: múltiples análisis en paralelo
            {"$facet": {

                # Sub-pipeline A: $bucket por rango de precio
                "distribucionPrecios": [
                    {"$bucket": {
                        "groupBy": "$precioReferencia",
                        "boundaries": [0, 50_000, 200_000, 500_000, 1_000_000],
                        "default": "Más de 1M",
                        "output": {
                            "cantidad": {"$sum": 1},
                            "precioPromedio": {"$avg": "$precioReferencia"},
                            "materiales": {"$push": "$nombre"},
                        },
                    }},
                ],

                # Sub-pipeline B: por unidad de medida
                "porUnidad": [
                    {"$group": {
                        "_id": "$unidadNormalizada",
                        "cantidad": {"$sum": 1},
                        "precioPromedio": {"$avg": "$precioReferencia"},
                    }},
                    {"$sort": {"cantidad": -1}},
                ],

                # Sub-pipeline C: por estado con $count
                "porEstado": [
                    {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
                ],

                # Sub-pipeline D: total general
                "totales": [
                    {"$count": "totalMateriales"},
                ],
            }},
        ]
        results = await self.collection.aggregate(pipeline).to_list(1)
        return results[0] if results else {}