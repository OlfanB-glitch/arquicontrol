from collections import Counter

from app.modules.clientes.infrastructure.repository import ClienteRepository
from app.modules.proyectos.application.service import proyecto_service
from app.modules.proyectos.infrastructure.repository import ProyectoRepository


class DashboardService:
    def __init__(self):
        self.client_repository = ClienteRepository()
        self.project_repository = ProyectoRepository()

    async def get_summary(self, user_id: str) -> dict:
        # 🔹 Idealmente estos métodos también deberían filtrar por user_id
        clients = await self.client_repository.list_all(user_id)
        projects = await proyecto_service.list_all(user_id)
        payments = await proyecto_service.get_payments_feed(user_id)
        purchases = await proyecto_service.get_purchases_feed(user_id)

        status_counter = Counter(project.estadoProyecto for project in projects)

        balances = [
            {
                "projectId": project.id,
                "projectName": project.nombreProyecto,
                "codigoProyecto": project.codigoProyecto,
                "saldoPendiente": project.resumenFinanciero.saldoPendienteCliente,
            }
            for project in projects
        ]

        project_progress = [
            {
                "projectId": project.id,
                "projectName": project.nombreProyecto,
                "codigoProyecto": project.codigoProyecto,
                "estadoProyecto": project.estadoProyecto,
                "porcentajeAvanceGeneral": project.porcentajeAvanceGeneral,
            }
            for project in projects
        ]

        alerts = []
        eventos_recientes = []

        for project in projects:
            for alert in project.alertas:
                alerts.append(
                    {
                        "projectId": project.id,
                        "projectName": project.nombreProyecto,
                        "codigoProyecto": project.codigoProyecto,
                        **alert.model_dump(),
                    }
                )

            for event in project.bitacora[:6]:
                eventos_recientes.append(
                    {
                        "projectId": project.id,
                        "projectName": project.nombreProyecto,
                        "codigoProyecto": project.codigoProyecto,
                        **event,
                    }
                )

        return {
            "totalClientes": len(clients),
            "totalProyectos": len(projects),
            "proyectosPorEstado": dict(status_counter),
            "saldoPendientePorProyecto": sorted(
                balances,
                key=lambda item: item["saldoPendiente"],
                reverse=True
            ),
            "pagosRecientes": payments,
            "comprasRecientes": purchases,
            "porcentajeAvanceGeneralPorProyecto": project_progress,
            "alertas": sorted(
                alerts,
                key=lambda item: item.get("createdAt", ""),
                reverse=True
            ),
            "eventosRecientes": sorted(
                eventos_recientes,
                key=lambda item: item.get("fecha", ""),
                reverse=True
            )[:10],
        }


dashboard_service = DashboardService()