"""
Sub-servicio de reportes: exportaciones PDF y CSV.

Extraído del ProyectoService original para mejorar la cohesión.
"""

import csv
from io import BytesIO, StringIO

from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.pdfgen import canvas # type: ignore

from app.modules.proyectos.application.project_helpers import format_currency, normalize_date_value


class ReportService:
    """Genera reportes PDF y CSV a partir de datos de proyecto ya resueltos."""

    def generate_client_summary_pdf(self, project: dict, client_name: str) -> dict:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y_position = height - 54

        def write_line(text: str, *, size: int = 10, bold: bool = False, gap: int = 16):
            nonlocal y_position
            if y_position < 60:
                pdf.showPage()
                y_position = height - 54
            pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            pdf.drawString(48, y_position, str(text)[:118])
            y_position -= gap

        pdf.setTitle(f"Resumen cliente {project['codigoProyecto']}")
        write_line("ArquiControl", size=12, bold=True, gap=18)
        write_line("Resumen de proyecto para cliente", size=18, bold=True, gap=24)
        write_line(f"Proyecto: {project['nombreProyecto']}", size=12, bold=True, gap=18)
        write_line(f"Código: {project['codigoProyecto']} · Cliente: {client_name}")
        write_line(f"Ubicación: {project['ubicacion']}")
        write_line(f"Estado actual: {project['estadoProyecto']} · Avance general: {project['porcentajeAvanceGeneral']}%")
        write_line(f"Periodo: {project['fechaInicio']} a {project['fechaFinEstimada']}")
        write_line("")
        write_line("Resumen financiero", size=12, bold=True, gap=18)
        write_line(f"Valor contrato: {format_currency(project['valorContrato'])}")
        write_line(f"Pagado por cliente: {format_currency(project['resumenFinanciero']['totalPagadoCliente'])}")
        write_line(f"Saldo pendiente: {format_currency(project['resumenFinanciero']['saldoPendienteCliente'])}")
        write_line(f"Costo ejecutado: {format_currency(project['resumenFinanciero']['costoTotalEjecutado'])}")
        write_line("")
        write_line("Fases activas", size=12, bold=True, gap=18)
        fases = project.get("fases", []) or []
        if fases:
            for fase in fases:
                write_line(f"• {fase['nombre']} · {fase['estado']} · avance {fase['porcentajeAvance']}%")
        else:
            write_line("• Sin fases activas registradas")
        write_line("")
        write_line("Hitos recientes", size=12, bold=True, gap=18)
        eventos = project.get("bitacora", [])[:5]
        if eventos:
            for event in eventos:
                write_line(
                    f"• {normalize_date_value(event.get('fecha')) or '—'} · {event.get('accion') or event.get('evento')} · {event.get('detalle') or 'Sin detalle'}",
                )
        else:
            write_line("• No hay eventos recientes en bitácora")

        pdf.save()
        content = buffer.getvalue()
        buffer.close()
        return {
            "filename": f"{project['codigoProyecto']}-resumen-cliente.pdf",
            "content": content,
            "media_type": "application/pdf",
        }

    def generate_financial_csv(self, project: dict, provider_names: dict[str, str]) -> dict:
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "categoria", "codigoProyecto", "proyecto", "fecha", "identificador",
            "detalle", "referencia", "monto", "estadoRegistro", "observaciones",
        ])

        rows = 0
        for payment in project.get("pagos", []):
            writer.writerow([
                "PAGO_CLIENTE", project["codigoProyecto"], project["nombreProyecto"],
                payment.get("fechaPago"), payment.get("idPago"),
                payment.get("concepto") or payment.get("tipoPago"),
                payment.get("referencia") or payment.get("metodoPago"),
                payment.get("monto", 0), "ACTIVO", payment.get("observaciones") or "",
            ])
            rows += 1
        for purchase in project.get("compras", []):
            writer.writerow([
                "COMPRA", project["codigoProyecto"], project["nombreProyecto"],
                purchase.get("fechaCompra"), purchase.get("idCompra"),
                provider_names.get(purchase.get("proveedorId"), "Proveedor no encontrado"),
                purchase.get("numeroFactura") or "", purchase.get("total", 0),
                "ACTIVO", purchase.get("observaciones") or "",
            ])
            rows += 1

        if not rows:
            writer.writerow([
                "SIN_MOVIMIENTOS", project["codigoProyecto"], project["nombreProyecto"],
                "", "", "", "", 0, "ACTIVO", "Sin pagos ni compras registradas",
            ])

        content = buffer.getvalue().encode("utf-8")
        buffer.close()
        return {
            "filename": f"{project['codigoProyecto']}-pagos-compras.csv",
            "content": content,
            "media_type": "text/csv; charset=utf-8",
        }

    def generate_contractor_payments_csv(self, project: dict, contractor_names: dict[str, str]) -> dict:
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "codigoProyecto", "proyecto", "contratista", "rol", "estadoAsignacion",
            "fechaPago", "referencia", "monto", "observaciones",
        ])

        rows = 0
        for assignment in project.get("contratistasAsignados", []):
            payments = assignment.get("pagosContratista", []) or []
            for payment in payments:
                writer.writerow([
                    project["codigoProyecto"], project["nombreProyecto"],
                    contractor_names.get(assignment.get("contratistaId"), "Contratista no encontrado"),
                    assignment.get("rol") or "", assignment.get("estado") or "",
                    payment.get("fechaPago") or "", payment.get("referencia") or "",
                    payment.get("monto", 0), payment.get("observaciones") or "",
                ])
                rows += 1

        if not rows:
            writer.writerow([
                project["codigoProyecto"], project["nombreProyecto"],
                "Sin pagos a contratistas", "", "", "", "", 0,
                "Aún no hay desembolsos registrados",
            ])

        content = buffer.getvalue().encode("utf-8")
        buffer.close()
        return {
            "filename": f"{project['codigoProyecto']}-pagos-contratistas.csv",
            "content": content,
            "media_type": "text/csv; charset=utf-8",
        }