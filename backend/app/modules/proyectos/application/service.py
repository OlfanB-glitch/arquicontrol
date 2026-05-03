"""
Servicio principal de proyectos — orquestador.

Refactorizado desde un monolito de 1 386 líneas a un orquestador que delega
responsabilidades a sub-servicios especializados:

  - project_helpers.py   → funciones puras (normalización, serialización, filtros, builders)
  - report_service.py    → exportaciones PDF y CSV
  - feed_service.py      → feeds transversales y bitácora

Este archivo conserva:
  - CRUD del agregado raíz (create, update, get_by_id, list_all)
  - Operaciones sobre subdocumentos (fases, seguimientos, pagos, contratistas, compras, documentos)
  - Instancia singleton `proyecto_service` consumida por el router
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.modules.clientes.infrastructure.repository import ClienteRepository
from app.modules.contratistas.infrastructure.repository import ContratistaRepository
from app.modules.materiales.infrastructure.repository import MaterialRepository
from app.modules.proveedores.infrastructure.repository import ProveedorRepository
from app.modules.proyectos.application.feed_service import FeedService
from app.modules.proyectos.application.project_helpers import (
    attach_document,
    base_lifecycle_metadata,
    build_assignment_record,
    build_document_entry,
    build_tracking_evidences,
    build_tracking_record,
    create_phase_record,
    mark_logical_delete,
    matches_project_filters,
    normalize_project,
    recalculate_project,
    require_assignment,
    require_document,
    require_payment,
    require_phase,
    require_purchase,
    require_tracking,
    serialize_project,
    set_event_context,
    validate_date_order,
    validate_project_status,
)
from app.modules.proyectos.application.report_service import ReportService
from app.modules.proyectos.domain.models import (
    AsignacionContratistaCreate,
    AsignacionContratistaUpdate,
    AvanceContratistaCreate,
    CompraCreate,
    CompraUpdate,
    DeleteEmbeddedRequest,
    DocumentoUpdate,
    DocumentoUrlCreate,
    FaseUpdate,
    PagoContratistaCreate,
    PagoCreate,
    PagoUpdate,
    ProyectoCreate,
    ProyectoResponse,
    ProyectoUpdate,
    SeguimientoCreate,
    SeguimientoUpdate,
)
from app.modules.proyectos.domain.observers import (
    AlertaPagosObserver,
    BitacoraProyectoObserver,
    IndicadoresProyectoObserver,
    ProyectoEventPublisher,
)
from app.modules.proyectos.domain.payment_factories import PagoFactoryResolver
from app.modules.proyectos.domain.strategies import AvanceStrategyResolver
from app.modules.proyectos.infrastructure.repository import ProyectoRepository
from app.shared.common import (
    create_audit_fields,
    generate_id,
    safe_filename,
    sum_amount,
    touch_updated_at,
    utc_now_iso,
)


ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".docx", ".xlsx", ".txt", ".md"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class ProyectoService:
    """Orquestador del módulo de proyectos."""

    def __init__(self, repository: ProyectoRepository):
        self.repository = repository
        self.cliente_repository = ClienteRepository()
        self.contratista_repository = ContratistaRepository()
        self.proveedor_repository = ProveedorRepository()
        self.material_repository = MaterialRepository()
        self.avance_resolver = AvanceStrategyResolver()
        self.pago_factory_resolver = PagoFactoryResolver()
        self.event_publisher = ProyectoEventPublisher([
            BitacoraProyectoObserver(),
            IndicadoresProyectoObserver(),
            AlertaPagosObserver(),
        ])
        self.report_service = ReportService()
        self.feed_service = FeedService(repository, self.cliente_repository, self.avance_resolver)

    # ------------------------------------------------------------------ #
    #  Consultas
    # ------------------------------------------------------------------ #

    async def list_all(self, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None) -> list[ProyectoResponse]:
        client_names = await self._client_name_map()
        projects = await self.repository.list_all()
        filtered = []
        for project in projects:
            normalized = normalize_project(project)
            recalculate_project(normalized, self.avance_resolver)
            if not matches_project_filters(normalized, client_names, q=q, estado=estado, cliente_id=cliente_id, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, monto_min=monto_min, monto_max=monto_max):
                continue
            filtered.append(ProyectoResponse(**serialize_project(normalized)))
        return filtered

    async def get_by_id(self, project_id: str, include_inactive: bool = False) -> ProyectoResponse:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        normalized = normalize_project(project)
        recalculate_project(normalized, self.avance_resolver)
        return ProyectoResponse(**serialize_project(normalized, include_inactive=include_inactive))

    # ------------------------------------------------------------------ #
    #  Bitácora y feeds (delegados a FeedService)
    # ------------------------------------------------------------------ #

    async def get_bitacora(self, project_id, fecha_desde=None, fecha_hasta=None, tipo_evento=None, usuario=None):
        return await self.feed_service.get_bitacora(project_id, fecha_desde, fecha_hasta, tipo_evento, usuario)

    async def list_bitacora(self, fecha_desde=None, fecha_hasta=None, tipo_evento=None, usuario=None, proyecto_id=None):
        return await self.feed_service.list_bitacora(fecha_desde, fecha_hasta, tipo_evento, usuario, proyecto_id)

    async def get_payments_feed(self, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None):
        return await self.feed_service.get_payments_feed(q, estado, cliente_id, fecha_desde, fecha_hasta, monto_min, monto_max)

    async def get_purchases_feed(self, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None):
        return await self.feed_service.get_purchases_feed(q, estado, cliente_id, fecha_desde, fecha_hasta, monto_min, monto_max)

    async def get_documents_feed(self, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None):
        return await self.feed_service.get_documents_feed(q, estado, cliente_id, fecha_desde, fecha_hasta, monto_min, monto_max)

    # ------------------------------------------------------------------ #
    #  Reportes (delegados a ReportService)
    # ------------------------------------------------------------------ #

    async def export_client_summary_pdf(self, project_id: str) -> dict:
        project = (await self.get_by_id(project_id)).model_dump()
        client_names = await self._client_name_map()
        client_name = client_names.get(project.get("clienteId"), "Cliente no encontrado")
        return self.report_service.generate_client_summary_pdf(project, client_name)

    async def export_project_financial_csv(self, project_id: str) -> dict:
        project = (await self.get_by_id(project_id)).model_dump()
        provider_names = {item["id"]: item["nombre"] for item in await self.proveedor_repository.list_all()}
        return self.report_service.generate_financial_csv(project, provider_names)

    async def export_contractor_payments_csv(self, project_id: str) -> dict:
        project = (await self.get_by_id(project_id)).model_dump()
        contractor_names = {item["id"]: item["nombreCompleto"] for item in await self.contratista_repository.list_all()}
        return self.report_service.generate_contractor_payments_csv(project, contractor_names)

    # ------------------------------------------------------------------ #
    #  CRUD del agregado raíz
    # ------------------------------------------------------------------ #

    async def create(self, payload: ProyectoCreate, actor: str) -> ProyectoResponse:
        await self._validate_project_base(payload)
        existing = await self.repository.get_by_code(payload.codigoProyecto)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de proyecto ya registrado")
        project = {
            **payload.model_dump(exclude={"fases"}),
            **create_audit_fields(),
            "fases": [create_phase_record(fase.model_dump()) for fase in payload.fases],
            "seguimientos": [], "pagos": [], "contratistasAsignados": [],
            "compras": [], "documentos": [], "resumenFinanciero": {},
            "bitacora": [], "alertas": [], "indicadores": {},
        }
        recalculate_project(project, self.avance_resolver)
        set_event_context(project, target="proyecto")
        self.event_publisher.notify("PROYECTO_CREADO", project, actor)
        created = await self.repository.create(project)
        return ProyectoResponse(**serialize_project(created))

    async def update(self, project_id: str, payload: ProyectoUpdate, actor: str) -> ProyectoResponse:
        current = await self._get_mutable_project(project_id)
        await self._validate_project_base(payload, current_project_id=project_id)
        existing = await self.repository.get_by_code(payload.codigoProyecto)
        if existing and existing["id"] != project_id:
            raise HTTPException(status_code=409, detail="Código de proyecto ya registrado")
        merged_phases = []
        existing_phases = [p for p in current.get("fases", []) if p.get("isActive", True)]
        inactive_phases = [p for p in current.get("fases", []) if not p.get("isActive", True)]
        for index, fase in enumerate(payload.fases):
            current_phase = existing_phases[index] if index < len(existing_phases) else None
            if current_phase:
                merged_phases.append({**current_phase, **fase.model_dump(), "updatedAt": utc_now_iso()})
            else:
                merged_phases.append(create_phase_record(fase.model_dump()))
        project = {**current, **payload.model_dump(exclude={"fases"}), "fases": [*merged_phases, *inactive_phases]}
        project = touch_updated_at(project)
        recalculate_project(project, self.avance_resolver)
        validate_project_status(project)
        set_event_context(project, target="proyecto")
        self.event_publisher.notify("PROYECTO_ACTUALIZADO", project, actor)
        saved = await self.repository.replace(project_id, project)
        return ProyectoResponse(**serialize_project(saved))

    # ------------------------------------------------------------------ #
    #  Subdocumentos: fases
    # ------------------------------------------------------------------ #

    async def update_phase(self, project_id: str, phase_id: str, payload: FaseUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        validate_date_order(payload.fechaInicio, payload.fechaFinEstimada, "fase")
        phase = require_phase(project, phase_id)
        phase.update(payload.model_dump())
        phase["updatedAt"] = utc_now_iso()
        return await self._save_and_notify(project, project_id, f"fase:{phase_id}", "FASE_ACTUALIZADA", actor)

    async def delete_phase(self, project_id: str, phase_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        phase = require_phase(project, phase_id)
        if any(item.get("faseId") == phase_id and item.get("isActive", True) for item in project.get("seguimientos", [])):
            raise HTTPException(status_code=409, detail="No se puede eliminar la fase con seguimientos activos")
        if any(item.get("faseId") == phase_id and item.get("isActive", True) for item in project.get("pagos", [])):
            raise HTTPException(status_code=409, detail="No se puede eliminar la fase con pagos activos")
        mark_logical_delete(phase, actor, payload.motivo, estado_inactivo="INACTIVA")
        return await self._save_and_notify(project, project_id, f"fase:{phase_id}", "FASE_ELIMINADA_LOGICAMENTE", actor, reason=payload.motivo)

    # ------------------------------------------------------------------ #
    #  Subdocumentos: seguimientos
    # ------------------------------------------------------------------ #

    async def add_tracking(self, project_id: str, payload: SeguimientoCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        require_phase(project, payload.faseId)
        tracking = build_tracking_record(payload.model_dump())
        project.setdefault("seguimientos", []).insert(0, tracking)
        return await self._save_and_notify(project, project_id, f"seguimiento:{tracking['id']}", "SEGUIMIENTO_REGISTRADO", actor)

    async def update_tracking(self, project_id: str, tracking_id: str, payload: SeguimientoUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        require_phase(project, payload.faseId)
        tracking = require_tracking(project, tracking_id)
        tracking.update({**payload.model_dump(exclude={"evidencias"}), "evidencias": build_tracking_evidences(payload.evidencias), "updatedAt": utc_now_iso()})
        return await self._save_and_notify(project, project_id, f"seguimiento:{tracking_id}", "SEGUIMIENTO_ACTUALIZADO", actor)

    async def delete_tracking(self, project_id: str, tracking_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        tracking = require_tracking(project, tracking_id)
        mark_logical_delete(tracking, actor, payload.motivo)
        for evidence in tracking.get("evidencias", []):
            mark_logical_delete(evidence, actor, payload.motivo)
        return await self._save_and_notify(project, project_id, f"seguimiento:{tracking_id}", "SEGUIMIENTO_ELIMINADO_LOGICAMENTE", actor, reason=payload.motivo)

    # ------------------------------------------------------------------ #
    #  Subdocumentos: pagos
    # ------------------------------------------------------------------ #

    async def add_payment(self, project_id: str, payload: PagoCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        if payload.faseId:
            require_phase(project, payload.faseId)
        payment = self._build_payment_record(payload)
        project.setdefault("pagos", []).insert(0, payment)
        return await self._save_and_notify(project, project_id, f"pago:{payment['idPago']}", "PAGO_REGISTRADO", actor)

    async def update_payment(self, project_id: str, payment_id: str, payload: PagoUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        payment = require_payment(project, payment_id)
        if payload.faseId:
            require_phase(project, payload.faseId)
        updated_payment = self._build_payment_record(payload, existing_payment=payment)
        for index, item in enumerate(project.get("pagos", [])):
            if item.get("idPago") == payment_id:
                project["pagos"][index] = updated_payment
                break
        return await self._save_and_notify(project, project_id, f"pago:{payment_id}", "PAGO_ACTUALIZADO", actor)

    async def delete_payment(self, project_id: str, payment_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        payment = require_payment(project, payment_id)
        mark_logical_delete(payment, actor, payload.motivo)
        return await self._save_and_notify(project, project_id, f"pago:{payment_id}", "PAGO_ELIMINADO_LOGICAMENTE", actor, reason=payload.motivo)

    # ------------------------------------------------------------------ #
    #  Subdocumentos: contratistas
    # ------------------------------------------------------------------ #

    async def add_contractor_assignment(self, project_id: str, payload: AsignacionContratistaCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        contractor = await self.contratista_repository.get_by_id(payload.contratistaId)
        if not contractor:
            raise HTTPException(status_code=404, detail="Contratista no encontrado")
        validate_date_order(payload.fechaInicio, payload.fechaFin, "asignación")
        assignment = build_assignment_record(payload.model_dump())
        project.setdefault("contratistasAsignados", []).append(assignment)
        return await self._save_and_notify(project, project_id, f"contratista:{assignment['idAsignacion']}", "CONTRATISTA_ASIGNADO", actor)

    async def update_assignment(self, project_id: str, assignment_id: str, payload: AsignacionContratistaUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        assignment = require_assignment(project, assignment_id)
        contractor = await self.contratista_repository.get_by_id(payload.contratistaId)
        if not contractor:
            raise HTTPException(status_code=404, detail="Contratista no encontrado")
        validate_date_order(payload.fechaInicio, payload.fechaFin, "asignación")
        assignment.update(payload.model_dump())
        assignment["updatedAt"] = utc_now_iso()
        return await self._save_and_notify(project, project_id, f"contratista:{assignment_id}", "ASIGNACION_CONTRATISTA_ACTUALIZADA", actor)

    async def delete_assignment(self, project_id: str, assignment_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        assignment = require_assignment(project, assignment_id)
        if assignment.get("avances") or assignment.get("pagosContratista"):
            raise HTTPException(status_code=409, detail="No se puede eliminar la asignación con avances o pagos de contratista registrados")
        mark_logical_delete(assignment, actor, payload.motivo, estado_inactivo="SUSPENDIDA")
        return await self._save_and_notify(project, project_id, f"contratista:{assignment_id}", "ASIGNACION_CONTRATISTA_ELIMINADA_LOGICAMENTE", actor, reason=payload.motivo)

    async def add_contractor_progress(self, project_id: str, assignment_id: str, payload: AvanceContratistaCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        assignment = require_assignment(project, assignment_id)
        assignment.setdefault("avances", []).insert(0, {"id": generate_id(), **payload.model_dump()})
        return await self._save_and_notify(project, project_id, f"avance_contratista:{assignment_id}", "AVANCE_CONTRATISTA_REGISTRADO", actor)

    async def add_contractor_payment(self, project_id: str, assignment_id: str, payload: PagoContratistaCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        assignment = require_assignment(project, assignment_id)
        assignment.setdefault("pagosContratista", []).insert(0, {"id": generate_id(), **payload.model_dump()})
        return await self._save_and_notify(project, project_id, f"pago_contratista:{assignment_id}", "PAGO_CONTRATISTA_REGISTRADO", actor)

    # ------------------------------------------------------------------ #
    #  Subdocumentos: compras
    # ------------------------------------------------------------------ #

    async def add_purchase(self, project_id: str, payload: CompraCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        purchase = await self._build_purchase_record(payload)
        project.setdefault("compras", []).insert(0, purchase)
        return await self._save_and_notify(project, project_id, f"compra:{purchase['idCompra']}", "COMPRA_REGISTRADA", actor)

    async def update_purchase(self, project_id: str, purchase_id: str, payload: CompraUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        purchase = require_purchase(project, purchase_id)
        updated_purchase = await self._build_purchase_record(payload, existing_purchase=purchase)
        for index, item in enumerate(project.get("compras", [])):
            if item.get("idCompra") == purchase_id:
                project["compras"][index] = updated_purchase
                break
        return await self._save_and_notify(project, project_id, f"compra:{purchase_id}", "COMPRA_ACTUALIZADA", actor)

    async def delete_purchase(self, project_id: str, purchase_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        purchase = require_purchase(project, purchase_id)
        mark_logical_delete(purchase, actor, payload.motivo)
        return await self._save_and_notify(project, project_id, f"compra:{purchase_id}", "COMPRA_ELIMINADA_LOGICAMENTE", actor, reason=payload.motivo)

    # ------------------------------------------------------------------ #
    #  Subdocumentos: documentos
    # ------------------------------------------------------------------ #

    async def add_document_url(self, project_id: str, payload: DocumentoUrlCreate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        document = build_document_entry(name=payload.nombre, url=payload.url, document_type=payload.tipo, source="URL", seguimiento_id=payload.seguimientoId, observations=payload.observaciones)
        attach_document(project, document)
        return await self._save_and_notify(project, project_id, f"documento:{document['id']}", "DOCUMENTO_REGISTRADO", actor)

    async def update_document(self, project_id: str, document_id: str, payload: DocumentoUpdate, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        found = require_document(project, document_id)
        document = found["document"]
        if payload.seguimientoId:
            require_tracking(project, payload.seguimientoId)
        updated_document = {**document, "nombre": payload.nombre, "url": payload.url, "tipo": payload.tipo, "seguimientoId": payload.seguimientoId, "observaciones": payload.observaciones, "updatedAt": utc_now_iso()}
        found["container"].remove(document)
        attach_document(project, updated_document)
        return await self._save_and_notify(project, project_id, f"documento:{document_id}", "DOCUMENTO_ACTUALIZADO", actor)

    async def delete_document(self, project_id: str, document_id: str, payload: DeleteEmbeddedRequest, actor: str) -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        found = require_document(project, document_id)
        mark_logical_delete(found["document"], actor, payload.motivo)
        return await self._save_and_notify(project, project_id, f"documento:{document_id}", "DOCUMENTO_ELIMINADO_LOGICAMENTE", actor, reason=payload.motivo)

    async def add_document_upload(self, project_id: str, file: UploadFile, document_type: str, actor: str, seguimiento_id: str | None = None, observations: str = "") -> ProyectoResponse:
        project = await self._get_mutable_project(project_id)
        if seguimiento_id:
            require_tracking(project, seguimiento_id)
        if not file.filename:
            raise HTTPException(status_code=400, detail="El archivo es obligatorio")
        extension = Path(file.filename).suffix.lower()
        if extension not in ALLOWED_UPLOAD_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Tipo de archivo no permitido para documentos del proyecto")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="El archivo no puede estar vacío")
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="El archivo supera el tamaño máximo permitido")
        stored_name = safe_filename(file.filename)
        destination = Path(settings.uploads_dir) / stored_name
        destination.write_bytes(content)
        document = build_document_entry(name=file.filename, url=f"/api/files/{stored_name}", document_type=document_type, source="ARCHIVO", seguimiento_id=seguimiento_id, observations=observations)
        attach_document(project, document)
        return await self._save_and_notify(project, project_id, f"documento:{document['id']}", "ARCHIVO_CARGADO", actor)

    # ------------------------------------------------------------------ #
    #  Métodos internos
    # ------------------------------------------------------------------ #

    async def _save_and_notify(self, project: dict, project_id: str, target: str, event: str, actor: str, reason: str | None = None) -> ProyectoResponse:
        """Patrón común: recalcular → notificar observers → persistir → serializar."""
        project = touch_updated_at(project)
        recalculate_project(project, self.avance_resolver)
        validate_project_status(project)
        set_event_context(project, target=target, reason=reason)
        self.event_publisher.notify(event, project, actor)
        saved = await self.repository.replace(project_id, project)
        return ProyectoResponse(**serialize_project(saved))

    async def _get_mutable_project(self, project_id: str) -> dict:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return normalize_project(project)

    async def _validate_project_base(self, payload: ProyectoCreate | ProyectoUpdate, current_project_id: str | None = None):
        del current_project_id
        client = await self.cliente_repository.get_by_id(payload.clienteId)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        validate_date_order(payload.fechaInicio, payload.fechaFinEstimada, "proyecto")
        for phase in payload.fases:
            validate_date_order(phase.fechaInicio, phase.fechaFinEstimada, "fase")

    def _build_payment_record(self, payload: PagoCreate | PagoUpdate, existing_payment: dict | None = None) -> dict:
        factory = self.pago_factory_resolver.resolve(payload.tipoPago)
        payment = factory.create(payload)
        meta = base_lifecycle_metadata() if not existing_payment else {
            key: existing_payment.get(key) for key in ["isActive", "deletedAt", "deletedBy", "motivo", "updatedAt"]
        }
        payment.update(meta)
        if existing_payment:
            payment["idPago"] = existing_payment["idPago"]
        payment["updatedAt"] = utc_now_iso()
        return payment

    async def _build_purchase_record(self, payload: CompraCreate | CompraUpdate, existing_purchase: dict | None = None) -> dict:
        provider = await self.proveedor_repository.get_by_id(payload.proveedorId)
        if not provider:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        details = []
        for item in payload.detalleCompra:
            material = await self.material_repository.get_by_id(item.materialId)
            if not material:
                raise HTTPException(status_code=404, detail="Uno de los materiales no existe")
            subtotal = round(item.cantidad * item.precioUnitario, 2)
            details.append({"idDetalle": generate_id(), **item.model_dump(), "subtotal": subtotal})
        subtotal = sum_amount(details, "subtotal")
        total = round(subtotal + payload.impuesto, 2)
        base = existing_purchase or base_lifecycle_metadata()
        return {
            **base,
            "idCompra": existing_purchase.get("idCompra") if existing_purchase else generate_id(),
            "proveedorId": payload.proveedorId, "fechaCompra": payload.fechaCompra,
            "numeroFactura": payload.numeroFactura, "subtotal": subtotal, "impuesto": payload.impuesto,
            "total": total, "observaciones": payload.observaciones, "detalleCompra": details,
            "updatedAt": utc_now_iso(),
        }

    async def _client_name_map(self) -> dict[str, str]:
        clients = await self.cliente_repository.list_all()
        return {item["id"]: item["nombreCompleto"] for item in clients}


# Instancia singleton consumida por el router
proyecto_service = ProyectoService(ProyectoRepository())