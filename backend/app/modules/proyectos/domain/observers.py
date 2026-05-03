from abc import ABC, abstractmethod
from datetime import date

from app.shared.catalogs import EstadoAsignacion, EstadoProyecto
from app.shared.common import generate_id, utc_now_iso


class ProyectoObserver(ABC):
    @abstractmethod
    def handle(self, event_name: str, project_data: dict, actor: str):
        raise NotImplementedError


class BitacoraProyectoObserver(ProyectoObserver):
    def handle(self, event_name: str, project_data: dict, actor: str):
        bitacora = list(project_data.get("bitacora", []))
        context = project_data.get("eventContext") or {}
        target = context.get("target", "proyecto")
        reason = context.get("reason")
        target_parts = str(target).split(":", 1)
        subrecord_type = target_parts[0]
        subrecord_id = target_parts[1] if len(target_parts) > 1 else project_data.get("id")
        action = context.get("action") or event_name
        detail = f"Evento {event_name} aplicado sobre {target} del proyecto {project_data.get('codigoProyecto')}"
        if reason:
            detail = f"{detail}. Motivo: {reason}"
        bitacora.insert(
            0,
            {
                "id": generate_id(),
                "evento": event_name,
                "tipoEvento": event_name,
                "modulo": "proyectos",
                "subregistroTipo": subrecord_type,
                "subregistroId": subrecord_id,
                "accion": action,
                "actor": actor,
                "usuario": actor,
                "motivo": reason,
                "fecha": utc_now_iso(),
                "detalle": detail,
            },
        )
        project_data["bitacora"] = bitacora[:25]


class IndicadoresProyectoObserver(ProyectoObserver):
    def handle(self, event_name: str, project_data: dict, actor: str):
        active_contractors = len(
            [
                item
                for item in project_data.get("contratistasAsignados", [])
                if item.get("estado") == EstadoAsignacion.ACTIVA and item.get("isActive", True)
            ],
        )
        active_trackings = [item for item in project_data.get("seguimientos", []) if item.get("isActive", True)]
        active_payments = [item for item in project_data.get("pagos", []) if item.get("isActive", True)]
        active_purchases = [item for item in project_data.get("compras", []) if item.get("isActive", True)]
        project_data["indicadores"] = {
            "ultimoEvento": event_name,
            "actualizadoPor": actor,
            "contratistasActivos": active_contractors,
            "seguimientosRegistrados": len(active_trackings),
            "pagosRegistrados": len(active_payments),
            "comprasRegistradas": len(active_purchases),
            "porcentajeAvanceGeneral": project_data.get("porcentajeAvanceGeneral", 0),
            "saldoPendienteCliente": project_data.get("resumenFinanciero", {}).get("saldoPendienteCliente", 0),
            "costoTotalEjecutado": project_data.get("resumenFinanciero", {}).get("costoTotalEjecutado", 0),
        }


class AlertaPagosObserver(ProyectoObserver):
    def handle(self, event_name: str, project_data: dict, actor: str):
        alerts = []
        summary = project_data.get("resumenFinanciero", {})
        saldo = float(summary.get("saldoPendienteCliente", 0) or 0)
        valor_contrato = float(project_data.get("valorContrato", 0) or 0)

        if saldo > max(valor_contrato * 0.1, 1):
            alerts.append(
                {
                    "id": generate_id(),
                    "tipo": "ALERTA_PAGO",
                    "nivel": "ALTO",
                    "mensaje": f"Saldo pendiente de {saldo:,.2f} en el proyecto.",
                    "createdAt": utc_now_iso(),
                },
            )

        try:
            due_date = date.fromisoformat(project_data.get("fechaFinEstimada", ""))
            if due_date < date.today() and project_data.get("estadoProyecto") not in {
                EstadoProyecto.FINALIZADO,
                EstadoProyecto.ENTREGADO,
            }:
                alerts.append(
                    {
                        "id": generate_id(),
                        "tipo": "PROYECTO_ATRASADO",
                        "nivel": "MEDIO",
                        "mensaje": "La fecha estimada del proyecto ya expiró.",
                        "createdAt": utc_now_iso(),
                    },
                )
        except ValueError:
            pass

        project_data["alertas"] = alerts
        project_data.pop("eventContext", None)


class ProyectoEventPublisher:
    def __init__(self, observers: list[ProyectoObserver]):
        self.observers = observers

    def notify(self, event_name: str, project_data: dict, actor: str):
        for observer in self.observers:
            observer.handle(event_name, project_data, actor)