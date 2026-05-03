import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Banknote, BriefcaseBusiness, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { AuditTimeline } from "@/components/shared/AuditTimeline";
import { MetricCard } from "@/components/shared/MetricCard";
import { ModuleTable } from "@/components/shared/ModuleTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { SectionCard } from "@/components/shared/SectionCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import api from "@/lib/api";
import { statusBarColors } from "@/lib/catalogs";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get("/dashboard/summary").then((response) => setSummary(response.data));
  }, []);

  const chartData = useMemo(
    () => Object.entries(summary?.proyectosPorEstado || {}).map(([name, value]) => ({ name, value })),
    [summary],
  );

  if (!summary) {
    return <div className="rounded-sm border border-zinc-200 bg-white p-8 text-sm text-zinc-600" data-testid="dashboard-loading-state">Cargando métricas del estudio...</div>;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        kicker="Vista ejecutiva"
        title="Dashboard principal"
        description="Resume el estado actual del portafolio, pagos del cliente, compras y alertas operativas de ArquiControl."
      />

      <div className="grid gap-6 xl:grid-cols-4 md:grid-cols-2">
        <MetricCard title="Clientes" value={summary.totalClientes} detail="Relaciones activas centralizadas" icon={Users} color="blue" href="/clientes" testId="dashboard-metric-clientes" />
        <MetricCard title="Proyectos" value={summary.totalProyectos} detail="Agregados raíz en seguimiento" icon={BriefcaseBusiness} color="purple" href="/proyectos" testId="dashboard-metric-proyectos" />
        <MetricCard title="Alertas" value={summary.alertas.length} detail="Pagos y fechas críticas detectadas" icon={AlertTriangle} color={summary.alertas.length > 0 ? "red" : "green"} href="/bitacora" testId="dashboard-metric-alertas" />
        <MetricCard title="Pagos recientes" value={summary.pagosRecientes.length} detail="Movimientos de cliente registrados" icon={Banknote} color="green" href="/pagos" testId="dashboard-metric-pagos" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
        <SectionCard title="Proyectos por estado" description="Lectura rápida del embudo operativo y avance del portafolio." testId="dashboard-status-chart-card" accent="blue">
          <div className="space-y-4" data-testid="dashboard-status-chart">
            {chartData.map((item) => {
              const maxValue = Math.max(...chartData.map((entry) => entry.value), 1);
              const width = `${Math.max((item.value / maxValue) * 100, 12)}%`;
              const barColor = statusBarColors[item.name] || "bg-zinc-500";

              return (
                <div key={item.name} className="space-y-2" data-testid={`dashboard-status-row-${item.name}`}>
                  <div className="flex items-center justify-between gap-4 text-sm text-zinc-700">
                    <div className="flex items-center gap-2">
                      <StatusBadge value={item.name} testId={`dashboard-status-badge-${item.name}`} />
                    </div>
                    <span className="font-semibold">{item.value}</span>
                  </div>
                  <div className="h-8 rounded-sm border border-zinc-200 bg-zinc-50 p-1">
                    <div className={`flex h-full items-center justify-end rounded-sm px-3 text-sm font-semibold text-white transition-all duration-500 ${barColor}`} style={{ width }}>
                      {item.value}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </SectionCard>

        <SectionCard title="Alertas activas" description="Eventos creados por observadores sobre el agregado proyecto." testId="dashboard-alerts-card" accent={summary.alertas.length > 0 ? "red" : "green"}>
          <div className="space-y-3">
            {summary.alertas.length ? summary.alertas.slice(0, 5).map((alert) => {
              const isHigh = alert.nivel === "ALTO";
              const borderColor = isHigh ? "border-red-300 bg-red-50" : "border-amber-300 bg-amber-50";
              return (
                <div key={alert.id} className={`rounded-sm border p-4 ${borderColor}`} data-testid={`dashboard-alert-row-${alert.id}`}>
                  <div className="flex items-center justify-between gap-3">
                    <StatusBadge value={alert.tipo} testId={`dashboard-alert-badge-${alert.id}`} />
                    <span className="text-xs text-zinc-500" data-testid={`dashboard-alert-date-${alert.id}`}>{formatDate(alert.createdAt)}</span>
                  </div>
                  <p className={`mt-3 text-sm font-medium ${isHigh ? "text-red-800" : "text-amber-800"}`} data-testid={`dashboard-alert-message-${alert.id}`}>{alert.mensaje}</p>
                  <p className="mt-2 text-xs uppercase tracking-[0.12em] text-zinc-500" data-testid={`dashboard-alert-project-${alert.id}`}>{alert.codigoProyecto}</p>
                </div>
              );
            }) : (
              <div className="rounded-sm border border-emerald-200 bg-emerald-50 p-6 text-center">
                <p className="text-lg font-semibold text-emerald-700">✓ Sin alertas activas</p>
                <p className="mt-2 text-sm text-emerald-600">Todos los proyectos operan dentro de los parámetros normales.</p>
              </div>
            )}
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="Bitácora reciente"
        description="Resumen ejecutivo de los últimos eventos operativos registrados por auditoría."
        actions={<Link to="/bitacora" className="inline-flex items-center rounded-sm border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-100" data-testid="dashboard-audit-open-link">Abrir módulo de bitácora</Link>}
        testId="dashboard-audit-card"
        accent="purple"
      >
        <AuditTimeline events={summary.eventosRecientes || []} compact emptyMessage="Todavía no hay eventos recientes para mostrar en el dashboard." />
      </SectionCard>

      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title="Saldo pendiente por proyecto" description="Ayuda a controlar cierres, flujo de caja y restricciones de entrega." testId="dashboard-balances-card" accent="amber">
          <ModuleTable
            items={summary.saldoPendientePorProyecto}
            columns={[
              { key: "codigoProyecto", label: "Código" },
              { key: "projectName", label: "Proyecto" },
              { key: "saldoPendiente", label: "Saldo", render: (item) => {
                const isHigh = item.saldoPendiente > 0;
                return <span className={`font-semibold ${isHigh ? "text-amber-700" : "text-emerald-700"}`} data-testid={`dashboard-balance-value-${item.projectId}`}>{formatCurrency(item.saldoPendiente)}</span>;
              }},
            ]}
          />
        </SectionCard>

        <SectionCard title="Avance general por proyecto" description="Consolidado calculado por estrategia de fases o seguimientos." testId="dashboard-progress-card" accent="blue">
          <ModuleTable
            items={summary.porcentajeAvanceGeneralPorProyecto}
            columns={[
              { key: "codigoProyecto", label: "Código" },
              { key: "projectName", label: "Proyecto" },
              { key: "estadoProyecto", label: "Estado", render: (item) => <StatusBadge value={item.estadoProyecto} testId={`dashboard-progress-status-${item.projectId}`} /> },
              { key: "porcentajeAvanceGeneral", label: "Avance", render: (item) => {
                const progress = item.porcentajeAvanceGeneral || 0;
                const color = progress >= 80 ? "bg-emerald-500" : progress >= 50 ? "bg-blue-500" : progress >= 25 ? "bg-amber-500" : "bg-zinc-400";
                return (
                  <div className="flex items-center gap-2" data-testid={`dashboard-progress-value-${item.projectId}`}>
                    <div className="h-2 w-20 rounded-full bg-zinc-200">
                      <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${progress}%` }} />
                    </div>
                    <span className="text-sm font-semibold text-zinc-700">{progress}%</span>
                  </div>
                );
              }},
            ]}
          />
        </SectionCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title="Pagos recientes" description="Últimos movimientos ingresados por proyecto." testId="dashboard-payments-card" accent="green">
          <ModuleTable
            items={summary.pagosRecientes}
            columns={[
              { key: "codigoProyecto", label: "Código" },
              { key: "projectName", label: "Proyecto" },
              { key: "payment.fechaPago", label: "Fecha", render: (item) => formatDate(item.payment?.fechaPago) },
              { key: "payment.monto", label: "Monto", render: (item) => <span className="font-semibold text-emerald-700">{formatCurrency(item.payment?.monto)}</span> },
            ]}
          />
        </SectionCard>

        <SectionCard title="Compras recientes" description="Control de adquisiciones enlazadas a cada proyecto." testId="dashboard-purchases-card" accent="amber">
          <ModuleTable
            items={summary.comprasRecientes}
            columns={[
              { key: "codigoProyecto", label: "Código" },
              { key: "projectName", label: "Proyecto" },
              { key: "purchase.fechaCompra", label: "Fecha", render: (item) => formatDate(item.purchase?.fechaCompra) },
              { key: "purchase.total", label: "Total", render: (item) => <span className="font-semibold text-amber-700">{formatCurrency(item.purchase?.total)}</span> },
            ]}
          />
        </SectionCard>
      </div>
    </div>
  );
}