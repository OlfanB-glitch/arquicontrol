from app.core.database import get_database
from app.modules.proyectos.domain.repositories import IProyectoRepository


class ProyectoRepository(IProyectoRepository):
    def __init__(self):
        self.collection = get_database().proyectos

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("updatedAt", -1)
        return await cursor.to_list(500)

    async def get_by_id(self, project_id: str) -> dict | None:
        return await self.collection.find_one({"id": project_id}, {"_id": 0})

    async def get_by_code(self, project_code: str) -> dict | None:
        return await self.collection.find_one({"codigoProyecto": project_code}, {"_id": 0})

    async def create(self, project_data: dict) -> dict:
        await self.collection.insert_one(dict(project_data))
        return project_data

    async def replace(self, project_id: str, project_data: dict) -> dict | None:
        await self.collection.replace_one({"id": project_id}, dict(project_data), upsert=False)
        return await self.get_by_id(project_id)

    async def aggregate_recent_payments(self) -> list[dict]:
        pipeline = [
            {"$unwind": "$pagos"},
            {
                "$project": {
                    "_id": 0,
                    "projectId": "$id",
                    "projectName": "$nombreProyecto",
                    "codigoProyecto": 1,
                    "payment": "$pagos",
                },
            },
            {"$sort": {"payment.fechaPago": -1}},
            {"$limit": 20},
        ]
        return await self.collection.aggregate(pipeline).to_list(20)

    async def aggregate_recent_purchases(self) -> list[dict]:
        pipeline = [
            {"$unwind": "$compras"},
            {
                "$project": {
                    "_id": 0,
                    "projectId": "$id",
                    "projectName": "$nombreProyecto",
                    "codigoProyecto": 1,
                    "purchase": "$compras",
                },
            },
            {"$sort": {"purchase.fechaCompra": -1}},
            {"$limit": 20},
        ]
        return await self.collection.aggregate(pipeline).to_list(20)

    async def aggregate_documents(self) -> list[dict]:
        pipeline = [
            {"$unwind": {"path": "$documentos", "preserveNullAndEmptyArrays": False}},
            {
                "$project": {
                    "_id": 0,
                    "projectId": "$id",
                    "projectName": "$nombreProyecto",
                    "codigoProyecto": 1,
                    "document": "$documentos",
                },
            },
            {"$sort": {"document.fechaRegistro": -1}},
            {"$limit": 30},
        ]
        return await self.collection.aggregate(pipeline).to_list(30)