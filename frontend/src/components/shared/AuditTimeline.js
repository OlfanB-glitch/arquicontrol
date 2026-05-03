import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { formatDate } from "@/lib/utils";

function formatTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("es-CO", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatEventLabel(value = "") {
  return String(value)
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function AuditTimeline({ events, compact = false, emptyMessage = "No hay eventos de auditoría disponibles." }) {
  const [expandedId, setExpandedId] = useState("");
  const visibleEvents = useMemo(() => (compact ? events.slice(0, 6) : events), [compact, events]);

  if (!visibleEvents.length) {
    return <p className="text-sm text-zinc-600" data-testid="audit-timeline-empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="space-y-3" data-testid="audit-timeline-list">
      {visibleEvents.map((event) => {
        const isExpanded = expandedId === event.id;
        return (
          <div key={event.id} className="rounded-sm border border-zinc-200 bg-white p-4" data-testid={`audit-event-row-${event.id}`}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0 flex-1 space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge value={formatEventLabel(event.tipoEvento || event.evento)} testId={`audit-event-type-${event.id}`} />
                  <span className="text-xs uppercase tracking-[0.12em] text-zinc-500" data-testid={`audit-event-subrecord-${event.id}`}>
                    {event.subregistroTipo || "proyecto"}
                  </span>
                  <span className="text-xs uppercase tracking-[0.12em] text-zinc-500" data-testid={`audit-event-subrecord-id-${event.id}`}>
                    {event.subregistroId || "sin-id"}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs uppercase tracking-[0.12em] text-zinc-500">
                  <span data-testid={`audit-event-project-${event.id}`}>{event.projectName || event.codigoProyecto || "Proyecto"}</span>
                  <span data-testid={`audit-event-code-${event.id}`}>{event.codigoProyecto || "—"}</span>
                </div>
                <p className="text-sm font-semibold text-zinc-950" data-testid={`audit-event-action-${event.id}`}>
                  {formatEventLabel(event.accion || event.evento)}
                </p>
                <p className="text-xs text-zinc-500" data-testid={`audit-event-meta-${event.id}`}>
                  {formatDate(event.fecha)} · {formatTime(event.fecha)} · {event.usuario || event.actor}
                </p>
                <p className="line-clamp-2 text-sm text-zinc-700" data-testid={`audit-event-summary-${event.id}`}>
                  {event.resumenCambio || event.detalle || "Sin resumen de cambio disponible."}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                className="rounded-sm text-zinc-700 hover:bg-zinc-100"
                onClick={() => setExpandedId(isExpanded ? "" : event.id)}
                data-testid={`audit-event-toggle-${event.id}`}
              >
                {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </div>

            {isExpanded ? (
              <div className="mt-4 grid gap-3 border-t border-zinc-200 pt-4 text-sm text-zinc-700" data-testid={`audit-event-detail-${event.id}`}>
                <div className="grid gap-2 md:grid-cols-2">
                  <p data-testid={`audit-event-detail-datetime-${event.id}`}><span className="font-semibold text-zinc-900">Fecha y hora:</span> {formatDate(event.fecha)} · {formatTime(event.fecha)}</p>
                  <p data-testid={`audit-event-detail-user-${event.id}`}><span className="font-semibold text-zinc-900">Usuario:</span> {event.usuario || event.actor || "—"}</p>
                  <p data-testid={`audit-event-detail-project-${event.id}`}><span className="font-semibold text-zinc-900">Proyecto:</span> {event.projectName || event.codigoProyecto || "—"}</p>
                  <p data-testid={`audit-event-detail-type-${event.id}`}><span className="font-semibold text-zinc-900">Tipo de evento:</span> {formatEventLabel(event.tipoEvento || event.evento)}</p>
                  <p data-testid={`audit-event-detail-subrecord-${event.id}`}><span className="font-semibold text-zinc-900">Subregistro afectado:</span> {(event.subregistroTipo || "proyecto")} · {event.subregistroId || "—"}</p>
                  <p data-testid={`audit-event-detail-action-${event.id}`}><span className="font-semibold text-zinc-900">Acción ejecutada:</span> {formatEventLabel(event.accion || event.evento)}</p>
                  <p data-testid={`audit-event-detail-module-${event.id}`}><span className="font-semibold text-zinc-900">Módulo:</span> {event.modulo || "proyectos"}</p>
                  <p data-testid={`audit-event-detail-code-${event.id}`}><span className="font-semibold text-zinc-900">Código proyecto:</span> {event.codigoProyecto || "—"}</p>
                </div>
                <p data-testid={`audit-event-description-${event.id}`}><span className="font-semibold text-zinc-900">Resumen del cambio:</span> {event.resumenCambio || event.detalle || "Sin detalle adicional."}</p>
                {event.motivo ? <p className="rounded-sm border border-zinc-200 bg-zinc-50 px-3 py-2" data-testid={`audit-event-reason-${event.id}`}><span className="font-semibold text-zinc-900">Motivo:</span> {event.motivo}</p> : null}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}