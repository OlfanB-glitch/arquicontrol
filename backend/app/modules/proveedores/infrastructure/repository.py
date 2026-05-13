from app.core.database import get_database
from app.modules.proveedores.domain.repositories import IProveedorRepository


class ProveedorRepository(IProveedorRepository):
    def __init__(self):
        self.collection = get_database().proveedores

    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("nombre", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, proveedor_id: str) -> dict | None:
        return await self.collection.find_one({"id": proveedor_id}, {"_id": 0})

    async def get_by_nit(self, nit: str, user_id: str) -> dict | None:
        return await self.collection.find_one(
            {"nit": nit, "userId": user_id}, {"_id": 0},
        )

    async def create(self, data: dict) -> dict:
        await self.collection.insert_one(dict(data))
        return data

    async def update(self, proveedor_id: str, data: dict) -> dict | None:
        await self.collection.update_one({"id": proveedor_id}, {"$set": data})
        return await self.get_by_id(proveedor_id)

    async def aggregate_stats(self, user_id: str) -> dict:
        """
        Pipeline de estadísticas de proveedores usando:
          $addFields — agrega campo calculado de longitud del nombre
          $facet     — múltiples sub-pipelines en paralelo
          $count     — conteo de proveedores activos
        """
        pipeline = [
            {"$match": {"userId": user_id}},

            # $addFields: enriquece cada documento con campos derivados
            {"$addFields": {
                "tieneObservaciones": {
                    "$and": [
                        {"$ne": ["$observaciones", None]},
                        {"$ne": ["$observaciones", ""]},
                    ]
                },
                "nombreLargo": {"$gt": [{"$strLenCP": "$nombre"}, 20]},
            }},

            # $facet: múltiples análisis en una sola pasada
            {"$facet": {

                # Sub-pipeline A: conteo por estado con $count
                "porEstado": [
                    {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
                ],

                # Sub-pipeline B: solo activos
                "activos": [
                    {"$match": {"estado": "ACTIVO"}},
                    {"$count": "totalActivos"},
                ],

                # Sub-pipeline C: con observaciones
                "conObservaciones": [
                    {"$match": {"tieneObservaciones": True}},
                    {"$count": "cantidad"},
                ],

                # Sub-pipeline D: total de proveedores
                "totales": [
                    {"$count": "totalProveedores"},
                ],
            }},
        ]
        results = await self.collection.aggregate(pipeline).to_list(1)
        return results[0] if results else {}