import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { AuditTimeline } from "@/components/shared/AuditTimeline";
import { EmptyState } from "@/components/shared/EmptyState";
import { MetricCard } from "@/components/shared/MetricCard";
import { PageHeader } from "@/components/shared/PageHeader";
import { SectionCard } from "@/components/shared/SectionCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import { buildQueryString } from "@/lib/utils";

const baseFilters = {
  fechaDesde: "",
  fechaHasta: "",
  tipoEvento: "",
  usuario: "",
  proyectoId: "",
};

export default function AuditLogPage() {
  const [events, setEvents] = useState(null);
  const [projects, setProjects] = useState([]);
  const [draftFilters, setDraftFilters] = useState(baseFilters);
  const [filters, setFilters] = useState(baseFilters);

  useEffect(() => {
    async function loadData() {
      const query = buildQueryString(filters);
      const [eventsResponse, projectsResponse] = await Promise.all([
        api.get(`/bitacora${query}`),
        api.get("/proyectos"),
      ]);
      setEvents(eventsResponse.data);
      setProjects(projectsResponse.data);
    }

    loadData();
  }, [filters]);

  const eventTypes = useMemo(
    () => Array.from(new Set((events || []).map((event) => event.tipoEvento || event.evento))).sort(),
    [events],
  );

  const impactedProjects = useMemo(
    () => new Set((events || []).map((event) => event.projectId).filter(Boolean)).size,
    [events],
  );

  const activeUsers = useMemo(
    () => new Set((events || []).map((event) => event.usuario || event.actor).filter(Boolean)).size,
    [events],
  );

  if (!events) {
    return <div className="rounded-sm border border-zinc-200 bg-white p-8 text-sm text-zinc-600" data-testid="audit-page-loading-state">Cargando bitácora operativa...</div>;
  }

  return (
    <div className="space-y-8" data-testid="audit-log-page">
      <PageHeader
        kicker="Auditoría transversal"
        title="Bitácora operativa"
        description="Consulta la trazabilidad técnica del estudio con filtros por fecha, evento, usuario y proyecto."
        actions={<Link to="/dashboard" className="inline-flex items-center rounded-sm border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-100" data-testid="audit-log-back-dashboard-link">Volver al dashboard</Link>}
      />

      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard title="Eventos visibles" value={events.length} detail="Registros filtrados disponibles" testId="audit-log-metric-events" />
        <MetricCard title="Proyectos impactados" value={impactedProjects} detail="Agregados con eventos en el corte actual" testId="audit-log-metric-projects" />
        <MetricCard title="Usuarios activos" value={activeUsers} detail="Actores detectados en la trazabilidad" testId="audit-log-metric-users" />
      </div>

      <SectionCard title="Filtros de auditoría" description="Aplica criterios técnicos para depurar la bitácora global." testId="audit-log-filters-card">
        <form
          className="grid gap-3 lg:grid-cols-5"
          onSubmit={(event) => {
            event.preventDefault();
            setFilters({ ...draftFilters });
          }}
          data-testid="audit-log-filter-form"
        >
          <Input type="date" value={draftFilters.fechaDesde} onChange={(event) => setDraftFilters((current) => ({ ...current, fechaDesde: event.target.value }))} data-testid="audit-log-filter-date-from" />
          <Input type="date" value={draftFilters.fechaHasta} onChange={(event) => setDraftFilters((current) => ({ ...current, fechaHasta: event.target.value }))} data-testid="audit-log-filter-date-to" />
          <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={draftFilters.tipoEvento} onChange={(event) => setDraftFilters((current) => ({ ...current, tipoEvento: event.target.value }))} data-testid="audit-log-filter-event-type">
            <option value="">Todos los eventos</option>
            {eventTypes.map((eventType) => <option key={eventType} value={eventType}>{`${eventType}`}</option>)}
          </select>
          <Input type="text" placeholder="Usuario" value={draftFilters.usuario} onChange={(event) => setDraftFilters((current) => ({ ...current, usuario: event.target.value }))} data-testid="audit-log-filter-user" />
          <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={draftFilters.proyectoId} onChange={(event) => setDraftFilters((current) => ({ ...current, proyectoId: event.target.value }))} data-testid="audit-log-filter-project">
            <option value="">Todos los proyectos</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{`${project.codigoProyecto} · ${project.nombreProyecto}`}</option>)}
          </select>
          <div className="flex gap-2 lg:col-span-5">
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="audit-log-filter-apply-button">Aplicar filtros</Button>
            <Button
              type="button"
              variant="outline"
              className="rounded-sm border-zinc-300"
              onClick={() => {
                setDraftFilters(baseFilters);
                setFilters(baseFilters);
              }}
              data-testid="audit-log-filter-reset-button"
            >
              Limpiar filtros
            </Button>
          </div>
        </form>
      </SectionCard>

      <SectionCard title="Eventos de auditoría" description="Lista técnica por defecto con detalle expandible por cada evento." testId="audit-log-events-card">
        {events.length ? (
          <AuditTimeline events={events} emptyMessage="No se encontraron eventos de auditoría con los filtros actuales." />
        ) : (
          <EmptyState title="Sin eventos para este corte" description="Ajusta los filtros o registra nuevas operaciones para alimentar la bitácora." />
        )}
      </SectionCard>
    </div>
  );
}