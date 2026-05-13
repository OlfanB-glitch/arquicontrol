from collections import Counter

from app.modules.clientes.infrastructure.repository import ClienteRepository
from app.modules.proyectos.application.service import proyecto_service
from app.modules.proyectos.infrastructure.repository import ProyectoRepository


class DashboardService:
    def __init__(self):
        self.client_repository = ClienteRepository()
        self.project_repository = ProyectoRepository()

    async def get_summary(self, user_id: str) -> dict:
        # Consultas en paralelo: datos básicos + pipeline avanzado
        clients = await self.client_repository.list_all(user_id)
        projects = await proyecto_service.list_all(user_id)
        payments = await proyecto_service.get_payments_feed(user_id)
        purchases = await proyecto_service.get_purchases_feed(user_id)

        # Pipeline avanzado: $addFields + $facet + $count + $bucket
        # Ejecuta todo en una sola query a MongoDB en lugar de Python loops
        advanced_stats = await self.project_repository.aggregate_dashboard_stats(user_id)

        # Extraer resultados de las facetas
        por_estado_raw = advanced_stats.get("porEstado", [])
        resumen_financiero = advanced_stats.get("resumenFinanciero", [{}])
        distribucion_contrato = advanced_stats.get("distribucionPorContrato", [])
        por_tipo = advanced_stats.get("porTipo", [])
        proyectos_atrasados = advanced_stats.get("atrasados", [])

        # Construir mapa de proyectos por estado desde el pipeline ($facet)
        proyectos_por_estado = {item["_id"]: item["total"] for item in por_estado_raw if item["_id"]}

        # Resumen financiero global calculado en MongoDB (no en Python)
        financiero = resumen_financiero[0] if resumen_financiero else {}

        # Distribución por rango de contrato ($bucket)
        rangos_contrato = []
        labels = ["0 - 50M", "50M - 150M", "150M - 300M", "300M - 600M", "Más de 600M"]
        for i, bucket in enumerate(distribucion_contrato):
            rangos_contrato.append({
                "rango": labels[i] if i < len(labels) else str(bucket.get("_id", "")),
                "cantidad": bucket.get("cantidad", 0),
                "valorTotal": bucket.get("valorTotal", 0),
            })

        # Datos que aún se calculan desde los objetos del proyecto
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
                alerts.append({
                    "projectId": project.id,
                    "projectName": project.nombreProyecto,
                    "codigoProyecto": project.codigoProyecto,
                    **alert.model_dump(),
                })
            for event in project.bitacora[:6]:
                eventos_recientes.append({
                    "projectId": project.id,
                    "projectName": project.nombreProyecto,
                    "codigoProyecto": project.codigoProyecto,
                    **event,
                })

        return {
            "totalClientes": len(clients),
            "totalProyectos": len(projects),
            "proyectosPorEstado": dict(status_counter),

            # Nuevos datos del pipeline avanzado
            "estadisticasAvanzadas": {
                "porEstado": [
                    {
                        "estado": item["_id"],
                        "total": item["total"],
                        "avancePromedio": round(item.get("avanceProm", 0) or 0, 1),
                    }
                    for item in por_estado_raw if item["_id"]
                ],
                "resumenFinanciero": {
                    "valorTotalContratos": financiero.get("valorTotalContratos", 0),
                    "totalPagadoClientes": financiero.get("totalPagadoClientes", 0),
                    "totalSaldoPendiente": financiero.get("totalSaldoPendiente", 0),
                    "totalCostoEjecutado": financiero.get("totalCostoEjecutado", 0),
                },
                "distribucionPorContrato": rangos_contrato,
                "porTipoProyecto": [
                    {"tipo": item["_id"], "cantidad": item["cantidad"]}
                    for item in por_tipo if item["_id"]
                ],
                "proyectosAtrasados": proyectos_atrasados,
            },

            "saldoPendientePorProyecto": sorted(
                balances, key=lambda item: item["saldoPendiente"], reverse=True
            ),
            "pagosRecientes": payments,
            "comprasRecientes": purchases,
            "porcentajeAvanceGeneralPorProyecto": project_progress,
            "alertas": sorted(alerts, key=lambda item: item.get("createdAt", ""), reverse=True),
            "eventosRecientes": sorted(
                eventos_recientes, key=lambda item: item.get("fecha", ""), reverse=True
            )[:10],
        }


dashboard_service = DashboardService()