from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response

from app.core.config import settings
from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
from app.modules.proyectos.application.service import proyecto_service
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


router = APIRouter(tags=["proyectos"])


@router.get("/proyectos", response_model=list[ProyectoResponse])
async def list_projects(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.list_all(q, estado, clienteId, fechaDesde, fechaHasta, montoMin, montoMax)


@router.post("/proyectos", response_model=ProyectoResponse)
async def create_project(
    payload: ProyectoCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.create(payload, current_user.email)


@router.get("/proyectos/{project_id}", response_model=ProyectoResponse)
async def get_project(project_id: str, _: UserResponse = Depends(get_current_user)):
    return await proyecto_service.get_by_id(project_id)


@router.get("/proyectos/{project_id}/bitacora")
async def get_project_bitacora(
    project_id: str,
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    tipoEvento: str | None = Query(default=None),
    usuario: str | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.get_bitacora(project_id, fechaDesde, fechaHasta, tipoEvento, usuario)


@router.get("/bitacora")
async def list_bitacora(
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    tipoEvento: str | None = Query(default=None),
    usuario: str | None = Query(default=None),
    proyectoId: str | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.list_bitacora(fechaDesde, fechaHasta, tipoEvento, usuario, proyectoId)


@router.get("/proyectos/{project_id}/reportes/resumen-cliente.pdf")
async def export_project_client_summary(project_id: str, _: UserResponse = Depends(get_current_user)):
    report = await proyecto_service.export_client_summary_pdf(project_id)
    return Response(
        content=report["content"],
        media_type=report["media_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{report["filename"]}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/proyectos/{project_id}/reportes/pagos-compras.csv")
async def export_project_payments_purchases(project_id: str, _: UserResponse = Depends(get_current_user)):
    report = await proyecto_service.export_project_financial_csv(project_id)
    return Response(
        content=report["content"],
        media_type=report["media_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{report["filename"]}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/proyectos/{project_id}/reportes/contratistas.csv")
async def export_project_contractor_payments(project_id: str, _: UserResponse = Depends(get_current_user)):
    report = await proyecto_service.export_contractor_payments_csv(project_id)
    return Response(
        content=report["content"],
        media_type=report["media_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{report["filename"]}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.put("/proyectos/{project_id}", response_model=ProyectoResponse)
async def update_project(
    project_id: str,
    payload: ProyectoUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update(project_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/seguimientos", response_model=ProyectoResponse)
async def add_tracking(
    project_id: str,
    payload: SeguimientoCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_tracking(project_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/seguimientos/{tracking_id}", response_model=ProyectoResponse)
async def update_tracking(
    project_id: str,
    tracking_id: str,
    payload: SeguimientoUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_tracking(project_id, tracking_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/seguimientos/{tracking_id}", response_model=ProyectoResponse)
async def delete_tracking(
    project_id: str,
    tracking_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_tracking(project_id, tracking_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/fases/{phase_id}", response_model=ProyectoResponse)
async def update_phase(
    project_id: str,
    phase_id: str,
    payload: FaseUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_phase(project_id, phase_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/fases/{phase_id}", response_model=ProyectoResponse)
async def delete_phase(
    project_id: str,
    phase_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_phase(project_id, phase_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/pagos", response_model=ProyectoResponse)
async def add_payment(
    project_id: str,
    payload: PagoCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_payment(project_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/pagos/{payment_id}", response_model=ProyectoResponse)
async def update_payment(
    project_id: str,
    payment_id: str,
    payload: PagoUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_payment(project_id, payment_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/pagos/{payment_id}", response_model=ProyectoResponse)
async def delete_payment(
    project_id: str,
    payment_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_payment(project_id, payment_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/contratistas", response_model=ProyectoResponse)
async def add_assignment(
    project_id: str,
    payload: AsignacionContratistaCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_contractor_assignment(project_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/contratistas/{assignment_id}", response_model=ProyectoResponse)
async def update_assignment(
    project_id: str,
    assignment_id: str,
    payload: AsignacionContratistaUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_assignment(project_id, assignment_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/contratistas/{assignment_id}", response_model=ProyectoResponse)
async def delete_assignment(
    project_id: str,
    assignment_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_assignment(project_id, assignment_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/contratistas/{assignment_id}/avances", response_model=ProyectoResponse)
async def add_assignment_progress(
    project_id: str,
    assignment_id: str,
    payload: AvanceContratistaCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_contractor_progress(project_id, assignment_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/contratistas/{assignment_id}/pagos", response_model=ProyectoResponse)
async def add_assignment_payment(
    project_id: str,
    assignment_id: str,
    payload: PagoContratistaCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_contractor_payment(project_id, assignment_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/compras", response_model=ProyectoResponse)
async def add_purchase(
    project_id: str,
    payload: CompraCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_purchase(project_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/compras/{purchase_id}", response_model=ProyectoResponse)
async def update_purchase(
    project_id: str,
    purchase_id: str,
    payload: CompraUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_purchase(project_id, purchase_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/compras/{purchase_id}", response_model=ProyectoResponse)
async def delete_purchase(
    project_id: str,
    purchase_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_purchase(project_id, purchase_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/documentos/url", response_model=ProyectoResponse)
async def add_document_url(
    project_id: str,
    payload: DocumentoUrlCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_document_url(project_id, payload, current_user.email)


@router.put("/proyectos/{project_id}/documentos/{document_id}", response_model=ProyectoResponse)
async def update_document(
    project_id: str,
    document_id: str,
    payload: DocumentoUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.update_document(project_id, document_id, payload, current_user.email)


@router.delete("/proyectos/{project_id}/documentos/{document_id}", response_model=ProyectoResponse)
async def delete_document(
    project_id: str,
    document_id: str,
    payload: DeleteEmbeddedRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.delete_document(project_id, document_id, payload, current_user.email)


@router.post("/proyectos/{project_id}/documentos/upload", response_model=ProyectoResponse)
async def add_document_upload(
    project_id: str,
    tipo: str = Form(...),
    seguimientoId: str | None = Form(default=None),
    observaciones: str = Form(default=""),
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.add_document_upload(
        project_id,
        file,
        tipo,
        current_user.email,
        seguimiento_id=seguimientoId,
        observations=observaciones,
    )


@router.get("/pagos")
async def list_payments_feed(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.get_payments_feed(q, estado, clienteId, fechaDesde, fechaHasta, montoMin, montoMax)


@router.get("/compras")
async def list_purchases_feed(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.get_purchases_feed(q, estado, clienteId, fechaDesde, fechaHasta, montoMin, montoMax)


@router.get("/documentos")
async def list_documents_feed(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),
):
    return await proyecto_service.get_documents_feed(q, estado, clienteId, fechaDesde, fechaHasta, montoMin, montoMax)


@router.get("/files/{file_name}")
async def get_uploaded_file(
    file_name: str,
    _: UserResponse = Depends(get_current_user),
):
    file_path = Path(settings.uploads_dir) / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)