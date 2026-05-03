"""
Funciones auxiliares compartidas por los sub-servicios de proyectos.

Extraídas del ProyectoService original (1 386 líneas) como parte de la
refactorización para mejorar cohesión y facilitar el testing unitario.
"""

from copy import deepcopy

from fastapi import HTTPException

from app.shared.catalogs import EstadoProyecto
from app.shared.common import generate_id, sum_amount, utc_now_iso


# ------------------------------------------------------------------ #
#  Normalización y serialización del agregado Proyecto
# ------------------------------------------------------------------ #

def normalize_project(project: dict) -> dict:
    """Garantiza que todas las listas y objetos embebidos existan."""
    normalized = deepcopy(project)
    normalized.setdefault("fases", [])
    normalized.setdefault("seguimientos", [])
    normalized.setdefault("pagos", [])
    normalized.setdefault("contratistasAsignados", [])
    normalized.setdefault("compras", [])
    normalized.setdefault("documentos", [])
    normalized.setdefault("resumenFinanciero", {})
    normalized.setdefault("bitacora", [])
    normalized.setdefault("alertas", [])
    normalized.setdefault("indicadores", {})
    for collection_name in ["fases", "seguimientos", "pagos", "contratistasAsignados", "compras", "documentos"]:
        for item in normalized.get(collection_name, []):
            ensure_lifecycle_defaults(item)
            if collection_name == "seguimientos":
                item.setdefault("evidencias", [])
                for evidence in item.get("evidencias", []):
                    ensure_lifecycle_defaults(evidence)
            if collection_name == "contratistasAsignados":
                item.setdefault("avances", [])
                item.setdefault("pagosContratista", [])
    return normalized


def serialize_project(project: dict, include_inactive: bool = False) -> dict:
    """Prepara el proyecto para ser devuelto como respuesta JSON."""
    serialized = deepcopy(project)
    if not include_inactive:
        serialized["fases"] = active_items(serialized.get("fases", []))
        serialized["seguimientos"] = active_items(serialized.get("seguimientos", []))
        for tracking in serialized["seguimientos"]:
            tracking["evidencias"] = active_items(tracking.get("evidencias", []))
        serialized["pagos"] = active_items(serialized.get("pagos", []))
        serialized["contratistasAsignados"] = active_items(serialized.get("contratistasAsignados", []))
        serialized["compras"] = active_items(serialized.get("compras", []))
        serialized["documentos"] = active_items(serialized.get("documentos", []))
    return serialized


# ------------------------------------------------------------------ #
#  Recálculo financiero y de avance
# ------------------------------------------------------------------ #

def recalculate_project(project: dict, avance_resolver) -> None:
    """Recalcula porcentaje de avance y resumen financiero in-place."""
    active_trackings = active_items(project.get("seguimientos", []))
    phase_progress = {
        phase_id: max(
            [float(item.get("porcentajeAvance", 0)) for item in active_trackings if item.get("faseId") == phase_id] or [0],
        )
        for phase_id in [fase.get("id") for fase in active_items(project.get("fases", []))]
    }
    for phase in project.get("fases", []):
        if not phase.get("isActive", True):
            continue
        if phase.get("id") in phase_progress and phase_progress[phase["id"]] > 0:
            phase["porcentajeAvance"] = phase_progress[phase["id"]]

    strategy = avance_resolver.resolve(project.get("metodoCalculoAvance", "SEGUIMIENTOS"))
    project["porcentajeAvanceGeneral"] = strategy.calculate(project)

    active_payments = active_items(project.get("pagos", []))
    active_purchases = active_items(project.get("compras", []))
    active_assignments = active_items(project.get("contratistasAsignados", []))

    total_pagado = sum_amount(active_payments, "monto")
    total_compras = sum_amount(active_purchases, "total")
    total_pagado_contratistas = round(
        sum(sum_amount(item.get("pagosContratista", []), "monto") for item in active_assignments), 2,
    )
    costo_total = round(total_compras + total_pagado_contratistas, 2)
    saldo_pendiente = round(max(float(project.get("valorContrato", 0)) - total_pagado, 0), 2)
    margen = round(float(project.get("valorContrato", 0)) - costo_total, 2)

    project["resumenFinanciero"] = {
        "totalPagadoCliente": total_pagado,
        "saldoPendienteCliente": saldo_pendiente,
        "totalCompras": total_compras,
        "totalPagadoContratistas": total_pagado_contratistas,
        "costoTotalEjecutado": costo_total,
        "margenEstimado": margen,
    }


# ------------------------------------------------------------------ #
#  Validaciones del estado del proyecto
# ------------------------------------------------------------------ #

def validate_project_status(project: dict) -> None:
    """Impide cerrar un proyecto con saldo pendiente superior al 10 %."""
    if project.get("estadoProyecto") not in {EstadoProyecto.FINALIZADO, EstadoProyecto.ENTREGADO}:
        return
    saldo = float(project.get("resumenFinanciero", {}).get("saldoPendienteCliente", 0) or 0)
    valor_contrato = float(project.get("valorContrato", 0) or 0)
    if saldo > max(valor_contrato * 0.1, 1):
        raise HTTPException(status_code=422, detail="No se puede cerrar el proyecto con un saldo pendiente importante")


def validate_date_order(start_date: str | None, end_date: str | None, label: str) -> None:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail=f"La fecha inicial no puede ser mayor a la fecha final en {label}")


# ------------------------------------------------------------------ #
#  Lookups — buscar subdocumentos por ID
# ------------------------------------------------------------------ #

def require_phase(project: dict, phase_id: str) -> dict:
    phase = next((item for item in project.get("fases", []) if item.get("id") == phase_id), None)
    if not phase or not phase.get("isActive", True):
        raise HTTPException(status_code=404, detail="La fase indicada no existe o está inactiva")
    return phase


def require_tracking(project: dict, tracking_id: str) -> dict:
    tracking = next((item for item in project.get("seguimientos", []) if item.get("id") == tracking_id), None)
    if not tracking or not tracking.get("isActive", True):
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    return tracking


def require_payment(project: dict, payment_id: str) -> dict:
    payment = next((item for item in project.get("pagos", []) if item.get("idPago") == payment_id), None)
    if not payment or not payment.get("isActive", True):
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment


def require_assignment(project: dict, assignment_id: str) -> dict:
    assignment = next(
        (item for item in project.get("contratistasAsignados", []) if item.get("idAsignacion") == assignment_id), None,
    )
    if not assignment or not assignment.get("isActive", True):
        raise HTTPException(status_code=404, detail="Asignación de contratista no encontrada")
    return assignment


def require_purchase(project: dict, purchase_id: str) -> dict:
    purchase = next((item for item in project.get("compras", []) if item.get("idCompra") == purchase_id), None)
    if not purchase or not purchase.get("isActive", True):
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return purchase


def require_document(project: dict, document_id: str) -> dict:
    for document in project.get("documentos", []):
        if document.get("id") == document_id and document.get("isActive", True):
            return {"container": project["documentos"], "document": document}
    for tracking in project.get("seguimientos", []):
        for evidence in tracking.get("evidencias", []):
            if evidence.get("id") == document_id and evidence.get("isActive", True):
                return {"container": tracking["evidencias"], "document": evidence, "tracking": tracking}
    raise HTTPException(status_code=404, detail="Documento no encontrado")


# ------------------------------------------------------------------ #
#  Builders — construir subdocumentos nuevos
# ------------------------------------------------------------------ #

def base_lifecycle_metadata() -> dict:
    return {
        "isActive": True,
        "deletedAt": None,
        "deletedBy": None,
        "motivo": None,
        "updatedAt": utc_now_iso(),
    }


def create_phase_record(payload: dict) -> dict:
    return {"id": generate_id(), **payload, **base_lifecycle_metadata()}


def build_tracking_record(payload: dict) -> dict:
    return {
        "id": generate_id(),
        **payload,
        "evidencias": build_tracking_evidences(payload.get("evidencias", [])),
        **base_lifecycle_metadata(),
    }


def build_tracking_evidences(evidencias: list) -> list[dict]:
    built = []
    for item in evidencias:
        data = item.model_dump() if hasattr(item, "model_dump") else dict(item)
        built.append({
            "id": generate_id(),
            "tipo": "EVIDENCIA",
            "nombre": data["nombre"],
            "url": data["url"],
            "descripcion": data.get("descripcion", ""),
            "fuente": "URL",
            "fechaRegistro": utc_now_iso(),
            **base_lifecycle_metadata(),
        })
    return built


def build_assignment_record(payload: dict) -> dict:
    return {"idAsignacion": generate_id(), **payload, "avances": [], "pagosContratista": [], **base_lifecycle_metadata()}


def build_document_entry(
    name: str, url: str, document_type: str, source: str, seguimiento_id: str | None, observations: str,
) -> dict:
    return {
        "id": generate_id(),
        "nombre": name,
        "url": url,
        "tipo": document_type,
        "fuente": source,
        "seguimientoId": seguimiento_id,
        "observaciones": observations,
        "fechaRegistro": utc_now_iso(),
        **base_lifecycle_metadata(),
    }


def attach_document(project: dict, document: dict) -> None:
    if document.get("seguimientoId"):
        tracking = require_tracking(project, document["seguimientoId"])
        tracking.setdefault("evidencias", []).insert(0, document)
        return
    project.setdefault("documentos", []).insert(0, document)


def mark_logical_delete(item: dict, actor: str, motivo: str, estado_inactivo: str | None = None) -> None:
    item["isActive"] = False
    item["deletedAt"] = utc_now_iso()
    item["deletedBy"] = actor
    item["motivo"] = motivo or ""
    item["updatedAt"] = utc_now_iso()
    if estado_inactivo is not None:
        item["estado"] = estado_inactivo


def set_event_context(project: dict, target: str, reason: str | None = None, action: str | None = None) -> None:
    project["eventContext"] = {"target": target, "reason": reason, "action": action}


# ------------------------------------------------------------------ #
#  Filtros reutilizables
# ------------------------------------------------------------------ #

def active_items(items: list[dict]) -> list[dict]:
    return [item for item in items if item.get("isActive", True)]


def ensure_lifecycle_defaults(item: dict) -> None:
    item.setdefault("isActive", True)
    item.setdefault("deletedAt", None)
    item.setdefault("deletedBy", None)
    item.setdefault("motivo", None)
    item.setdefault("updatedAt", item.get("fechaRegistro") or utc_now_iso())


def normalize_date_value(value: str | None) -> str | None:
    if not value:
        return None
    return str(value)[:10]


def format_currency(value: float | int) -> str:
    amount = float(value or 0)
    return f"COP {amount:,.0f}"


def matches_search(text: str, q: str | None) -> bool:
    if not q:
        return True
    return q.strip().lower() in text


def matches_date_range(value: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> bool:
    if not value:
        return not fecha_desde and not fecha_hasta
    if fecha_desde and value < fecha_desde:
        return False
    if fecha_hasta and value > fecha_hasta:
        return False
    return True


def matches_amount(value: float, monto_min: float | None, monto_max: float | None) -> bool:
    if monto_min is not None and value < monto_min:
        return False
    if monto_max is not None and value > monto_max:
        return False
    return True


def matches_bitacora_filters(
    event: dict, fecha_desde: str | None, fecha_hasta: str | None, tipo_evento: str | None, usuario: str | None,
) -> bool:
    event_date = normalize_date_value(event.get("fecha"))
    event_type = event.get("tipoEvento", event.get("evento"))
    actor = str(event.get("usuario", event.get("actor", ""))).lower()
    if tipo_evento and event_type != tipo_evento:
        return False
    if usuario and usuario.lower() not in actor:
        return False
    return matches_date_range(event_date, fecha_desde, fecha_hasta)


def matches_project_reference(project: dict, project_filter: str) -> bool:
    references = " ".join([
        str(project.get("id", "")),
        str(project.get("codigoProyecto", "")),
        str(project.get("nombreProyecto", "")),
    ]).lower()
    return project_filter in references


def matches_project_filters(
    project: dict, client_names: dict[str, str],
    q: str | None, estado: str | None, cliente_id: str | None,
    fecha_desde: str | None, fecha_hasta: str | None,
    monto_min: float | None, monto_max: float | None,
) -> bool:
    if estado and project.get("estadoProyecto") != estado:
        return False
    if cliente_id and project.get("clienteId") != cliente_id:
        return False
    if not matches_date_range(normalize_date_value(project.get("fechaInicio")), fecha_desde, fecha_hasta):
        return False
    if not matches_amount(float(project.get("valorContrato", 0) or 0), monto_min, monto_max):
        return False
    text = " ".join([
        project.get("codigoProyecto", ""),
        project.get("nombreProyecto", ""),
        project.get("descripcion", ""),
        project.get("ubicacion", ""),
        project.get("observacionesGenerales", ""),
        client_names.get(project.get("clienteId"), ""),
    ]).lower()
    return matches_search(text, q)


def matches_feed_filters(
    project: dict, client_names: dict[str, str],
    q: str | None, estado: str | None, cliente_id: str | None,
    fecha: str | None, amount: float,
    fecha_desde: str | None, fecha_hasta: str | None,
    monto_min: float | None, monto_max: float | None,
    extra_text: list[str | None],
) -> bool:
    if estado and project.get("estadoProyecto") != estado:
        return False
    if cliente_id and project.get("clienteId") != cliente_id:
        return False
    if not matches_date_range(fecha, fecha_desde, fecha_hasta):
        return False
    if not matches_amount(amount, monto_min, monto_max):
        return False
    text = " ".join([
        project.get("codigoProyecto", ""),
        project.get("nombreProyecto", ""),
        project.get("descripcion", ""),
        client_names.get(project.get("clienteId"), ""),
        *[item or "" for item in extra_text],
    ]).lower()
    return matches_search(text, q)


def enrich_bitacora_event(project: dict, event: dict) -> dict:
    enriched = deepcopy(event)
    enriched.setdefault("tipoEvento", event.get("evento"))
    enriched.setdefault("usuario", event.get("actor"))
    enriched.setdefault("actor", event.get("usuario"))
    enriched.setdefault("accion", event.get("tipoEvento") or event.get("evento"))
    enriched.setdefault("subregistroTipo", "proyecto")
    enriched.setdefault("subregistroId", project.get("id"))
    enriched["projectId"] = project.get("id")
    enriched["projectName"] = project.get("nombreProyecto")
    enriched["codigoProyecto"] = project.get("codigoProyecto")
    enriched["resumenCambio"] = event.get("detalle") or "Sin resumen disponible"
    return enriched