import { useState } from "react";
import { Pencil, Trash2, X } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { SectionCard } from "@/components/shared/SectionCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import api from "@/lib/api";
import { ASSIGNMENT_STATUSES } from "@/lib/catalogs";
import { formatCurrency } from "@/lib/utils";

const initialAssignment = { contratistaId: "", rol: "", fechaInicio: "", fechaFin: "", valorAcordado: 0, estado: ASSIGNMENT_STATUSES[0] };

export function ContractorsTab({ project, setProject, contractors, contractorMap, onRequestDelete }) {
  const [form, setForm] = useState({ ...initialAssignment, contratistaId: contractors[0]?.id || "" });
  const [editingId, setEditingId] = useState("");
  const [progressForm, setProgressForm] = useState({ assignmentId: project.contratistasAsignados?.[0]?.idAsignacion || "", fecha: "", descripcion: "", jornadaHoras: 0, porcentajeAvance: 0 });
  const [paymentForm, setPaymentForm] = useState({ assignmentId: project.contratistasAsignados?.[0]?.idAsignacion || "", fechaPago: "", monto: 0, referencia: "", observaciones: "" });

  function reset() {
    setEditingId("");
    setForm({ ...initialAssignment, contratistaId: contractors[0]?.id || "" });
  }

  function startEdit(assignment) {
    setEditingId(assignment.idAsignacion);
    setForm({ contratistaId: assignment.contratistaId, rol: assignment.rol, fechaInicio: assignment.fechaInicio, fechaFin: assignment.fechaFin || "", valorAcordado: assignment.valorAcordado, estado: assignment.estado });
  }

  async function submit(event) {
    event.preventDefault();
    const payload = { ...form, valorAcordado: Number(form.valorAcordado || 0) };
    try {
      const response = editingId ? await api.put(`/proyectos/${project.id}/contratistas/${editingId}`, payload) : await api.post(`/proyectos/${project.id}/contratistas`, payload);
      setProject(response.data);
      reset();
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  async function submitProgress(event) {
    event.preventDefault();
    try {
      const response = await api.post(`/proyectos/${project.id}/contratistas/${progressForm.assignmentId}/avances`, { fecha: progressForm.fecha, descripcion: progressForm.descripcion, jornadaHoras: Number(progressForm.jornadaHoras || 0), porcentajeAvance: Number(progressForm.porcentajeAvance || 0) });
      setProject(response.data);
      setProgressForm((c) => ({ ...c, fecha: "", descripcion: "", jornadaHoras: 0, porcentajeAvance: 0 }));
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  async function submitPayment(event) {
    event.preventDefault();
    try {
      const response = await api.post(`/proyectos/${project.id}/contratistas/${paymentForm.assignmentId}/pagos`, { fechaPago: paymentForm.fechaPago, monto: Number(paymentForm.monto || 0), referencia: paymentForm.referencia, observaciones: paymentForm.observaciones });
      setProject(response.data);
      setPaymentForm((c) => ({ ...c, fechaPago: "", monto: 0, referencia: "", observaciones: "" }));
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  return (
    <>
      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title={editingId ? "Editar asignación" : "Asignar contratista"} description="Vincula especialistas al proyecto con rol, rango de fechas y valor acordado." testId="project-assignment-card">
          <form className="grid gap-4" onSubmit={submit}>
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.contratistaId} onChange={(e) => setForm((c) => ({ ...c, contratistaId: e.target.value }))} data-testid="assignment-form-contractor-select">{contractors.map((contractor) => <option key={contractor.id} value={contractor.id}>{contractor.nombreCompleto}</option>)}</select>
            <Input type="text" placeholder="Rol" value={form.rol} onChange={(e) => setForm((c) => ({ ...c, rol: e.target.value }))} data-testid="assignment-form-role-input" />
            <Input type="date" value={form.fechaInicio} onChange={(e) => setForm((c) => ({ ...c, fechaInicio: e.target.value }))} data-testid="assignment-form-start-input" />
            <Input type="date" value={form.fechaFin} onChange={(e) => setForm((c) => ({ ...c, fechaFin: e.target.value }))} data-testid="assignment-form-end-input" />
            <Input type="number" placeholder="Valor acordado" value={form.valorAcordado} onChange={(e) => setForm((c) => ({ ...c, valorAcordado: e.target.value }))} data-testid="assignment-form-value-input" />
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.estado} onChange={(e) => setForm((c) => ({ ...c, estado: e.target.value }))} data-testid="assignment-form-status-select">{ASSIGNMENT_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}</select>
            <div className="flex justify-end gap-2">
              {editingId ? <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={reset} data-testid="assignment-form-cancel-button"><X className="h-4 w-4" /> Cancelar</Button> : null}
              <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="assignment-form-submit-button">{editingId ? "Actualizar" : "Asignar"}</Button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Registrar avance y pago" description="Los avances y pagos a contratista se mantienen sin reestructurar en esta fase." testId="project-contractor-actions-card">
          <div className="space-y-6">
            <form className="grid gap-4" onSubmit={submitProgress}>
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Nuevo avance</p>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={progressForm.assignmentId} onChange={(e) => setProgressForm((c) => ({ ...c, assignmentId: e.target.value }))} data-testid="contractor-progress-assignment-select">{project.contratistasAsignados.map((a) => <option key={a.idAsignacion} value={a.idAsignacion}>{contractorMap[a.contratistaId]} · {a.rol}</option>)}</select>
              <Input type="date" value={progressForm.fecha} onChange={(e) => setProgressForm((c) => ({ ...c, fecha: e.target.value }))} data-testid="contractor-progress-date-input" />
              <Input type="number" placeholder="Horas" value={progressForm.jornadaHoras} onChange={(e) => setProgressForm((c) => ({ ...c, jornadaHoras: e.target.value }))} data-testid="contractor-progress-hours-input" />
              <Input type="number" placeholder="% avance" value={progressForm.porcentajeAvance} onChange={(e) => setProgressForm((c) => ({ ...c, porcentajeAvance: e.target.value }))} data-testid="contractor-progress-percent-input" />
              <Textarea value={progressForm.descripcion} onChange={(e) => setProgressForm((c) => ({ ...c, descripcion: e.target.value }))} data-testid="contractor-progress-description-input" />
              <div className="flex justify-end"><Button type="submit" variant="outline" className="rounded-sm border-zinc-300" data-testid="contractor-progress-submit-button">Guardar avance</Button></div>
            </form>
            <form className="grid gap-4 border-t border-zinc-200 pt-6" onSubmit={submitPayment}>
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Nuevo pago contratista</p>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={paymentForm.assignmentId} onChange={(e) => setPaymentForm((c) => ({ ...c, assignmentId: e.target.value }))} data-testid="contractor-payment-assignment-select">{project.contratistasAsignados.map((a) => <option key={a.idAsignacion} value={a.idAsignacion}>{contractorMap[a.contratistaId]} · {a.rol}</option>)}</select>
              <Input type="date" value={paymentForm.fechaPago} onChange={(e) => setPaymentForm((c) => ({ ...c, fechaPago: e.target.value }))} data-testid="contractor-payment-date-input" />
              <Input type="number" placeholder="Monto" value={paymentForm.monto} onChange={(e) => setPaymentForm((c) => ({ ...c, monto: e.target.value }))} data-testid="contractor-payment-amount-input" />
              <Input type="text" placeholder="Referencia" value={paymentForm.referencia} onChange={(e) => setPaymentForm((c) => ({ ...c, referencia: e.target.value }))} data-testid="contractor-payment-reference-input" />
              <Textarea value={paymentForm.observaciones} onChange={(e) => setPaymentForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="contractor-payment-observations-input" />
              <div className="flex justify-end"><Button type="submit" variant="outline" className="rounded-sm border-zinc-300" data-testid="contractor-payment-submit-button">Guardar pago</Button></div>
            </form>
          </div>
        </SectionCard>
      </div>

      <div className="mt-6 grid gap-4">
        {project.contratistasAsignados.length ? project.contratistasAsignados.map((assignment) => (
          <div key={assignment.idAsignacion} className="rounded-sm border border-zinc-200 bg-white p-5" data-testid={`assignment-card-${assignment.idAsignacion}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-zinc-950">{contractorMap[assignment.contratistaId]}</h3>
                <p className="mt-1 text-sm text-zinc-600">{assignment.rol}</p>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startEdit(assignment)} data-testid={`assignment-edit-button-${assignment.idAsignacion}`}><Pencil className="h-4 w-4" /></Button>
                <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => onRequestDelete({ endpoint: `/proyectos/${project.id}/contratistas/${assignment.idAsignacion}`, label: `${contractorMap[assignment.contratistaId] || "Contratista"} · ${assignment.rol}`, type: "Asignación de contratista" })} data-testid={`assignment-delete-button-${assignment.idAsignacion}`}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </div>
            <div className="mt-4 grid gap-4 text-sm text-zinc-700 md:grid-cols-3">
              <div><span className="font-semibold text-zinc-900">Estado:</span> <StatusBadge value={assignment.estado} testId={`assignment-status-${assignment.idAsignacion}`} /></div>
              <div><span className="font-semibold text-zinc-900">Valor:</span> {formatCurrency(assignment.valorAcordado)}</div>
              <div><span className="font-semibold text-zinc-900">Avances/Pagos:</span> {assignment.avances.length} / {assignment.pagosContratista.length}</div>
            </div>
          </div>
        )) : <EmptyState title="Sin contratistas asignados" description="Asigna el primer contratista para controlar jornadas, avances y pagos internos del proyecto." />}
      </div>
    </>
  );
}
