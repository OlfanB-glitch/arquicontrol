"""
Sub-servicio de feeds transversales: pagos, compras, documentos y bitácora.

Extraído del ProyectoService original para mejorar la cohesión.
"""

from app.modules.proyectos.application.project_helpers import (
    active_items,
    enrich_bitacora_event,
    matches_bitacora_filters,
    matches_feed_filters,
    matches_project_reference,
    normalize_date_value,
    normalize_project,
    recalculate_project,
)


class FeedService:
    """Genera vistas transversales sobre subdocumentos de todos los proyectos."""

    def __init__(self, repository, cliente_repository, avance_resolver):
        self.repository = repository
        self.cliente_repository = cliente_repository
        self.avance_resolver = avance_resolver

    async def _client_name_map(self) -> dict[str, str]:
        clients = await self.cliente_repository.list_all()
        return {item["id"]: item["nombreCompleto"] for item in clients}

    async def get_payments_feed(
        self, user_id: str | None = None, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None,
    ) -> list[dict]:
        projects = await self.repository.list_all(user_id)
        client_names = await self._client_name_map()
        payments = []
        for project in projects:
            normalized = normalize_project(project)
            recalculate_project(normalized, self.avance_resolver)
            for payment in active_items(normalized.get("pagos", [])):
                if not matches_feed_filters(
                    normalized, client_names, q=q, estado=estado, cliente_id=cliente_id,
                    fecha=normalize_date_value(payment.get("fechaPago")),
                    amount=float(payment.get("monto", 0) or 0),
                    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
                    monto_min=monto_min, monto_max=monto_max,
                    extra_text=[payment.get("tipoPago"), payment.get("concepto"), payment.get("referencia")],
                ):
                    continue
                payments.append({
                    "projectId": normalized["id"],
                    "projectName": normalized["nombreProyecto"],
                    "codigoProyecto": normalized["codigoProyecto"],
                    "clienteId": normalized["clienteId"],
                    "clienteNombre": client_names.get(normalized.get("clienteId"), ""),
                    "estadoProyecto": normalized.get("estadoProyecto"),
                    "payment": payment,
                })
        payments.sort(key=lambda item: item["payment"].get("fechaPago", ""), reverse=True)
        return payments[:50]

    async def get_purchases_feed(
        self, user_id: str | None = None, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None,
    ) -> list[dict]:
        projects = await self.repository.list_all(user_id)
        client_names = await self._client_name_map()
        purchases = []
        for project in projects:
            normalized = normalize_project(project)
            recalculate_project(normalized, self.avance_resolver)
            for purchase in active_items(normalized.get("compras", [])):
                if not matches_feed_filters(
                    normalized, client_names, q=q, estado=estado, cliente_id=cliente_id,
                    fecha=normalize_date_value(purchase.get("fechaCompra")),
                    amount=float(purchase.get("total", 0) or 0),
                    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
                    monto_min=monto_min, monto_max=monto_max,
                    extra_text=[purchase.get("numeroFactura"), purchase.get("observaciones")],
                ):
                    continue
                purchases.append({
                    "projectId": normalized["id"],
                    "projectName": normalized["nombreProyecto"],
                    "codigoProyecto": normalized["codigoProyecto"],
                    "clienteId": normalized["clienteId"],
                    "clienteNombre": client_names.get(normalized.get("clienteId"), ""),
                    "estadoProyecto": normalized.get("estadoProyecto"),
                    "purchase": purchase,
                })
        purchases.sort(key=lambda item: item["purchase"].get("fechaCompra", ""), reverse=True)
        return purchases[:50]

    async def get_documents_feed(
        self, user_id: str | None = None, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None,
    ) -> list[dict]:
        projects = await self.repository.list_all(user_id)
        client_names = await self._client_name_map()
        documents = []
        for project in projects:
            normalized = normalize_project(project)
            recalculate_project(normalized, self.avance_resolver)
            project_documents = active_items(normalized.get("documentos", []))
            evidence_documents = []
            for tracking in active_items(normalized.get("seguimientos", [])):
                for evidence in active_items(tracking.get("evidencias", [])):
                    evidence_documents.append({**evidence, "seguimientoId": tracking.get("id")})
            for document in [*project_documents, *evidence_documents]:
                if not matches_feed_filters(
                    normalized, client_names, q=q, estado=estado, cliente_id=cliente_id,
                    fecha=normalize_date_value(document.get("fechaRegistro")),
                    amount=float(normalized.get("valorContrato", 0) or 0),
                    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
                    monto_min=monto_min, monto_max=monto_max,
                    extra_text=[document.get("nombre"), document.get("tipo"), document.get("observaciones")],
                ):
                    continue
                documents.append({
                    "projectId": normalized["id"],
                    "projectName": normalized["nombreProyecto"],
                    "codigoProyecto": normalized["codigoProyecto"],
                    "clienteId": normalized["clienteId"],
                    "clienteNombre": client_names.get(normalized.get("clienteId"), ""),
                    "estadoProyecto": normalized.get("estadoProyecto"),
                    "document": document,
                })
        documents.sort(key=lambda item: item["document"].get("fechaRegistro", ""), reverse=True)
        return documents[:50]

    async def get_bitacora(
        self, project_id: str, fecha_desde=None, fecha_hasta=None, tipo_evento=None, usuario=None,
        user_id=None,
    ) -> list[dict]:
        """Bitácora de un proyecto específico — usa pipeline de agregación de MongoDB."""
        from fastapi import HTTPException

        if not user_id:
            raise HTTPException(status_code=401, detail="Sesión requerida")

        results = await self.repository.aggregate_project_bitacora(
            project_id=project_id,
            user_id=user_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            tipo_evento=tipo_evento,
            usuario=usuario,
        )

        if not results:
            # Verificar si el proyecto existe (para dar 404 correcto)
            project = await self.repository.get_by_id(project_id, user_id)
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        # Enriquecer cada evento con los datos del proyecto
        return [
            {
                **item["event"],
                "projectId": item["projectId"],
                "projectName": item["projectName"],
                "codigoProyecto": item["codigoProyecto"],
                "tipoEvento": item["event"].get("tipoEvento") or item["event"].get("evento"),
                "usuario": item["event"].get("usuario") or item["event"].get("actor"),
                "actor": item["event"].get("actor") or item["event"].get("usuario"),
                "accion": item["event"].get("tipoEvento") or item["event"].get("evento"),
                "resumenCambio": item["event"].get("detalle") or "Sin resumen disponible",
            }
            for item in results
        ]

    async def list_bitacora(
        self, fecha_desde=None, fecha_hasta=None, tipo_evento=None, usuario=None, proyecto_id=None, user_id=None,
    ) -> list[dict]:
        """Bitácora global de todos los proyectos — usa pipeline de agregación de MongoDB."""
        results = await self.repository.aggregate_global_bitacora(
            user_id=user_id or "",
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            tipo_evento=tipo_evento,
            usuario=usuario,
            proyecto_id=proyecto_id,
        )

        # Enriquecer cada evento con los datos del proyecto
        return [
            {
                **item["event"],
                "projectId": item["projectId"],
                "projectName": item["projectName"],
                "codigoProyecto": item["codigoProyecto"],
                "tipoEvento": item["event"].get("tipoEvento") or item["event"].get("evento"),
                "usuario": item["event"].get("usuario") or item["event"].get("actor"),
                "actor": item["event"].get("actor") or item["event"].get("usuario"),
                "accion": item["event"].get("tipoEvento") or item["event"].get("evento"),
                "resumenCambio": item["event"].get("detalle") or "Sin resumen disponible",
            }
            for item in results
        ]