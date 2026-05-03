import { useMemo, useState } from "react";
import { ScrollText } from "lucide-react";

import { AuditTimeline } from "@/components/shared/AuditTimeline";
import { EmptyState } from "@/components/shared/EmptyState";
import { SectionCard } from "@/components/shared/SectionCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatDate } from "@/lib/utils";

export function AuditTab({ project }) {
  const [filters, setFilters] = useState({ fechaDesde: "", fechaHasta: "", tipoEvento: "", usuario: "" });

  const events = useMemo(
    () => (project?.bitacora || []).map((event) => ({ ...event, projectId: project?.id, projectName: project?.nombreProyecto, codigoProyecto: project?.codigoProyecto, resumenCambio: event.resumenCambio || event.detalle })),
    [project],
  );

  const eventTypes = useMemo(() => Array.from(new Set(events.map((e) => e.tipoEvento || e.evento))).sort(), [events]);

  const filtered = useMemo(() => events.filter((event) => {
    const eventDate = String(event.fecha || "").slice(0, 10);
    const actor = String(event.usuario || event.actor || "").toLowerCase();
    if (filters.fechaDesde && eventDate < filters.fechaDesde) return false;
    if (filters.fechaHasta && eventDate > filters.fechaHasta) return false;
    if (filters.tipoEvento && (event.tipoEvento || event.evento) !== filters.tipoEvento) return false;
    if (filters.usuario && !actor.includes(filters.usuario.toLowerCase())) return false;
    return true;
  }), [events, filters]);

  return (
    <SectionCard title="Auditoría operativa" description="Bitácora visible del proyecto con filtros técnicos y detalle expandible por evento." testId="project-audit-card">
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
          <div className="rounded-sm border border-zinc-200 bg-zinc-50 p-4" data-testid="project-audit-project-box">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Proyecto filtrado</p>
            <p className="mt-2 text-sm font-semibold text-zinc-950">{project.codigoProyecto}</p>
            <p className="mt-1 text-sm text-zinc-600">{project.nombreProyecto}</p>
          </div>
          <div className="rounded-sm border border-zinc-200 bg-zinc-50 p-4" data-testid="project-audit-events-count-box">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Eventos visibles</p>
            <p className="mt-2 text-2xl font-semibold text-zinc-950">{filtered.length}</p>
          </div>
          <div className="rounded-sm border border-zinc-200 bg-zinc-50 p-4" data-testid="project-audit-users-count-box">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Usuarios detectados</p>
            <p className="mt-2 text-2xl font-semibold text-zinc-950">{new Set(filtered.map((e) => e.usuario || e.actor).filter(Boolean)).size}</p>
          </div>
          <div className="rounded-sm border border-zinc-200 bg-zinc-50 p-4" data-testid="project-audit-last-event-box">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Último evento</p>
            <p className="mt-2 text-sm font-semibold text-zinc-950">{filtered[0]?.tipoEvento || filtered[0]?.evento || "Sin eventos"}</p>
            <p className="mt-1 text-sm text-zinc-600">{formatDate(filtered[0]?.fecha)}</p>
          </div>
        </div>

        <form className="grid gap-3 rounded-sm border border-zinc-200 bg-white p-4 lg:grid-cols-4 xl:grid-cols-5" data-testid="project-audit-filter-form">
          <Input type="date" value={filters.fechaDesde} onChange={(e) => setFilters((c) => ({ ...c, fechaDesde: e.target.value }))} data-testid="project-audit-filter-date-from" />
          <Input type="date" value={filters.fechaHasta} onChange={(e) => setFilters((c) => ({ ...c, fechaHasta: e.target.value }))} data-testid="project-audit-filter-date-to" />
          <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={filters.tipoEvento} onChange={(e) => setFilters((c) => ({ ...c, tipoEvento: e.target.value }))} data-testid="project-audit-filter-event-type">
            <option value="">Todos los eventos</option>
            {eventTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <Input type="text" placeholder="Usuario" value={filters.usuario} onChange={(e) => setFilters((c) => ({ ...c, usuario: e.target.value }))} data-testid="project-audit-filter-user" />
          <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => setFilters({ fechaDesde: "", fechaHasta: "", tipoEvento: "", usuario: "" })} data-testid="project-audit-filter-reset-button">Limpiar filtros</Button>
        </form>

        {filtered.length ? (
          <AuditTimeline events={filtered} emptyMessage="No hay eventos de auditoría para los filtros actuales." />
        ) : (
          <EmptyState title="Sin eventos en este corte" description="Ajusta filtros o ejecuta nuevas operaciones para alimentar la trazabilidad del proyecto." action={<div className="inline-flex items-center gap-2 rounded-sm border border-zinc-200 px-4 py-2 text-sm text-zinc-700" data-testid="project-audit-empty-action"><ScrollText className="h-4 w-4" /> Bitácora activa al registrar altas, ediciones y bajas</div>} />
        )}
      </div>
    </SectionCard>
  );
}
