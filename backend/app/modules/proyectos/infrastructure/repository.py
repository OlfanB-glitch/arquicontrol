from app.core.database import get_database
from app.modules.proyectos.domain.repositories import IProyectoRepository


class ProyectoRepository(IProyectoRepository):
    def __init__(self):
        self.collection = get_database().proyectos

    async def list_all(self, user_id: str) -> list[dict]:
        cursor = self.collection.find(
            {"userId": user_id},
            {"_id": 0}
        ).sort("updatedAt", -1)
        return await cursor.to_list(500)

    async def get_by_id(self, project_id: str, user_id: str | None = None) -> dict | None:
        query = {"id": project_id}
        if user_id:
            query["userId"] = user_id
        return await self.collection.find_one(query, {"_id": 0})

    async def get_by_code(self, project_code: str, user_id: str | None = None) -> dict | None:
        query = {"codigoProyecto": project_code}
        if user_id:
            query["userId"] = user_id
        return await self.collection.find_one(query, {"_id": 0})

    async def create(self, project_data: dict) -> dict:
        await self.collection.insert_one(dict(project_data))
        return project_data

    async def replace(self, project_id: str, user_id: str, project_data: dict) -> dict | None:
        await self.collection.replace_one(
            {"id": project_id, "userId": user_id},
            dict(project_data),
            upsert=False
        )
        return await self.get_by_id(project_id, user_id)

    async def aggregate_recent_payments(self, user_id: str) -> list[dict]:
        pipeline = [
            {"$match": {"userId": user_id}},  # 🔥 CLAVE
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

    async def aggregate_recent_purchases(self, user_id: str) -> list[dict]:
        pipeline = [
            {"$match": {"userId": user_id}},  # 🔥 CLAVE
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

    async def aggregate_documents(self, user_id: str) -> list[dict]:
        pipeline = [
            {"$match": {"userId": user_id}},  # 🔥 CLAVE
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

    async def aggregate_project_bitacora(
        self, project_id: str, user_id: str,
        fecha_desde: str | None = None, fecha_hasta: str | None = None,
        tipo_evento: str | None = None, usuario: str | None = None,
    ) -> list[dict]:
        """Pipeline de agregación para la bitácora de un proyecto específico."""
        match_stage = {"id": project_id, "userId": user_id}
        pipeline = [
            {"$match": match_stage},
            {"$unwind": {"path": "$bitacora", "preserveNullAndEmptyArrays": False}},
            {"$project": {
                "_id": 0,
                "projectId": "$id",
                "projectName": "$nombreProyecto",
                "codigoProyecto": "$codigoProyecto",
                "event": "$bitacora",
            }},
        ]
        # Filtros dinámicos sobre los campos del evento
        event_filters = {}
        if tipo_evento:
            event_filters["$or"] = [
                {"event.tipoEvento": tipo_evento},
                {"event.evento": tipo_evento},
            ]
        if usuario:
            event_filters["$or"] = event_filters.get("$or", []) or []
            # Usar regex para búsqueda parcial case-insensitive
            pipeline.append({"$match": {
                "$or": [
                    {"event.actor": {"$regex": usuario, "$options": "i"}},
                    {"event.usuario": {"$regex": usuario, "$options": "i"}},
                ],
            }}) if usuario else None
        if tipo_evento:
            pipeline.append({"$match": {
                "$or": [
                    {"event.tipoEvento": tipo_evento},
                    {"event.evento": tipo_evento},
                ],
            }})
        if fecha_desde:
            pipeline.append({"$match": {"event.fecha": {"$gte": fecha_desde}}})
        if fecha_hasta:
            pipeline.append({"$match": {"event.fecha": {"$lte": fecha_hasta + "T23:59:59Z"}}})

        pipeline.extend([
            {"$sort": {"event.fecha": -1}},
            {"$limit": 100},
        ])
        return await self.collection.aggregate(pipeline).to_list(100)

    async def aggregate_global_bitacora(
        self, user_id: str,
        fecha_desde: str | None = None, fecha_hasta: str | None = None,
        tipo_evento: str | None = None, usuario: str | None = None,
        proyecto_id: str | None = None,
    ) -> list[dict]:
        """Pipeline de agregación para la bitácora global de todos los proyectos."""
        match_stage: dict = {"userId": user_id}
        if proyecto_id:
            # Filtro flexible: busca por id, código o nombre
            match_stage["$or"] = [
                {"id": {"$regex": proyecto_id, "$options": "i"}},
                {"codigoProyecto": {"$regex": proyecto_id, "$options": "i"}},
                {"nombreProyecto": {"$regex": proyecto_id, "$options": "i"}},
            ]

        pipeline: list[dict] = [
            {"$match": match_stage},
            {"$unwind": {"path": "$bitacora", "preserveNullAndEmptyArrays": False}},
            {"$project": {
                "_id": 0,
                "projectId": "$id",
                "projectName": "$nombreProyecto",
                "codigoProyecto": "$codigoProyecto",
                "event": "$bitacora",
            }},
        ]

        # Filtros dinámicos
        if tipo_evento:
            pipeline.append({"$match": {
                "$or": [
                    {"event.tipoEvento": tipo_evento},
                    {"event.evento": tipo_evento},
                ],
            }})
        if usuario:
            pipeline.append({"$match": {
                "$or": [
                    {"event.actor": {"$regex": usuario, "$options": "i"}},
                    {"event.usuario": {"$regex": usuario, "$options": "i"}},
                ],
            }})
        if fecha_desde:
            pipeline.append({"$match": {"event.fecha": {"$gte": fecha_desde}}})
        if fecha_hasta:
            pipeline.append({"$match": {"event.fecha": {"$lte": fecha_hasta + "T23:59:59Z"}}})

        pipeline.extend([
            {"$sort": {"event.fecha": -1}},
            {"$limit": 250},
        ])
        return await self.collection.aggregate(pipeline).to_list(250)