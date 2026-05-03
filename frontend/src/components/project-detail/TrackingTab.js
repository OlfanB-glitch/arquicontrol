import { useState } from "react";
import { Link2, Pencil, Plus, Trash2, X } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { SectionCard } from "@/components/shared/SectionCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import api from "@/lib/api";
import { openDocumentResource } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const initialForm = { faseId: "", fecha: "", observaciones: "", porcentajeAvance: 0, evidenciaNombre: "", evidenciaUrl: "" };

export function TrackingTab({ project, setProject, onRequestDelete }) {
  const [form, setForm] = useState({ ...initialForm, faseId: project.fases?.[0]?.id || "" });
  const [editingId, setEditingId] = useState("");

  function reset() {
    setEditingId("");
    setForm({ ...initialForm, faseId: project.fases?.[0]?.id || "" });
  }

  function startEdit(tracking) {
    setEditingId(tracking.id);
    const firstEvidence = tracking.evidencias?.[0];
    setForm({ faseId: tracking.faseId, fecha: tracking.fecha, observaciones: tracking.observaciones, porcentajeAvance: tracking.porcentajeAvance, evidenciaNombre: firstEvidence?.nombre || "", evidenciaUrl: firstEvidence?.url || "" });
  }

  async function submit(event) {
    event.preventDefault();
    const payload = { faseId: form.faseId, fecha: form.fecha, observaciones: form.observaciones, porcentajeAvance: Number(form.porcentajeAvance || 0), evidencias: form.evidenciaNombre && form.evidenciaUrl ? [{ nombre: form.evidenciaNombre, url: form.evidenciaUrl, descripcion: form.observaciones }] : [] };
    try {
      const response = editingId ? await api.put(`/proyectos/${project.id}/seguimientos/${editingId}`, payload) : await api.post(`/proyectos/${project.id}/seguimientos`, payload);
      setProject(response.data);
      reset();
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  return (
    <>
      <SectionCard title={editingId ? "Editar seguimiento" : "Registrar seguimiento"} description="Asocia observaciones y evidencias a una fase existente del proyecto." testId="project-tracking-card">
        <form className="grid gap-4 lg:grid-cols-2" onSubmit={submit}>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Fase</span>
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.faseId} onChange={(e) => setForm((c) => ({ ...c, faseId: e.target.value }))} data-testid="tracking-form-phase-select">{project.fases.map((fase) => <option key={fase.id} value={fase.id}>{fase.nombre}</option>)}</select>
          </label>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Fecha</span>
            <Input type="date" value={form.fecha} onChange={(e) => setForm((c) => ({ ...c, fecha: e.target.value }))} data-testid="tracking-form-date-input" />
          </label>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">% avance</span>
            <Input type="number" value={form.porcentajeAvance} onChange={(e) => setForm((c) => ({ ...c, porcentajeAvance: e.target.value }))} data-testid="tracking-form-progress-input" />
          </label>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Nombre evidencia URL</span>
            <Input type="text" value={form.evidenciaNombre} onChange={(e) => setForm((c) => ({ ...c, evidenciaNombre: e.target.value }))} data-testid="tracking-form-evidence-name-input" />
          </label>
          <label className="lg:col-span-2">
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Observaciones</span>
            <Textarea value={form.observaciones} onChange={(e) => setForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="tracking-form-observations-input" />
          </label>
          <label className="lg:col-span-2">
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">URL evidencia</span>
            <Input type="url" value={form.evidenciaUrl} onChange={(e) => setForm((c) => ({ ...c, evidenciaUrl: e.target.value }))} data-testid="tracking-form-evidence-url-input" />
          </label>
          <div className="lg:col-span-2 flex justify-end gap-2">
            {editingId ? <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={reset} data-testid="tracking-form-cancel-button"><X className="h-4 w-4" /> Cancelar</Button> : null}
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="tracking-form-submit-button"><Plus className="h-4 w-4" /> {editingId ? "Actualizar seguimiento" : "Guardar seguimiento"}</Button>
          </div>
        </form>
      </SectionCard>

      <div className="mt-6 space-y-4">
        {project.seguimientos.length ? project.seguimientos.map((tracking) => (
          <div key={tracking.id} className="rounded-sm border border-zinc-200 bg-white p-5" data-testid={`tracking-card-${tracking.id}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">{project.fases.find((fase) => fase.id === tracking.faseId)?.nombre || "Fase"}</p>
                <h3 className="mt-2 text-base font-semibold text-zinc-950">{tracking.observaciones}</h3>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startEdit(tracking)} data-testid={`tracking-edit-button-${tracking.id}`}><Pencil className="h-4 w-4" /></Button>
                <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => onRequestDelete({ endpoint: `/proyectos/${project.id}/seguimientos/${tracking.id}`, label: `Seguimiento ${tracking.observaciones}`, type: "Seguimiento" })} data-testid={`tracking-delete-button-${tracking.id}`}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </div>
            <p className="mt-3 text-sm font-medium text-zinc-700">{tracking.porcentajeAvance}% · {formatDate(tracking.fecha)}</p>
            {tracking.evidencias?.length ? <div className="mt-4 flex flex-wrap gap-3">{tracking.evidencias.map((evidence) => <button key={evidence.id} type="button" onClick={() => openDocumentResource(evidence.url)} className="inline-flex items-center gap-2 rounded-sm border border-zinc-300 px-3 py-2 text-sm text-zinc-800 hover:bg-zinc-100" data-testid={`tracking-evidence-link-${evidence.id}`}><Link2 className="h-4 w-4" /> {evidence.nombre}</button>)}</div> : null}
          </div>
        )) : <EmptyState title="Sin seguimientos registrados" description="Agrega el primer seguimiento para comenzar la trazabilidad técnica del proyecto." />}
      </div>
    </>
  );
}
