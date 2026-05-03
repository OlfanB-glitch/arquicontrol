import { useState } from "react";
import { Pencil, Trash2, X } from "lucide-react";

import { SectionCard } from "@/components/shared/SectionCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import api from "@/lib/api";
import { PAYMENT_TYPES } from "@/lib/catalogs";
import { formatCurrency, formatDate } from "@/lib/utils";

const initialForm = { tipoPago: PAYMENT_TYPES[0], faseId: "", fechaPago: "", monto: 0, metodoPago: "TRANSFERENCIA", referencia: "", concepto: "", observaciones: "" };

export function PaymentsTab({ project, setProject, onRequestDelete }) {
  const [form, setForm] = useState({ ...initialForm, faseId: project.fases?.[0]?.id || "" });
  const [editingId, setEditingId] = useState("");

  function reset() {
    setEditingId("");
    setForm({ ...initialForm, faseId: project.fases?.[0]?.id || "" });
  }

  function startEdit(payment) {
    setEditingId(payment.idPago);
    setForm({ tipoPago: payment.tipoPago, faseId: payment.faseId || project.fases?.[0]?.id || "", fechaPago: payment.fechaPago, monto: payment.monto, metodoPago: payment.metodoPago, referencia: payment.referencia, concepto: payment.concepto, observaciones: payment.observaciones });
  }

  async function submit(event) {
    event.preventDefault();
    const payload = { ...form, faseId: form.tipoPago === "PAGO_POR_FASE" ? form.faseId : null, monto: Number(form.monto || 0) };
    try {
      const response = editingId ? await api.put(`/proyectos/${project.id}/pagos/${editingId}`, payload) : await api.post(`/proyectos/${project.id}/pagos`, payload);
      setProject(response.data);
      reset();
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  return (
    <>
      <SectionCard title={editingId ? "Editar pago" : "Registrar pago"} description="Usa factory method para crear anticipos, pagos generales o pagos por fase." testId="project-payments-card">
        <form className="grid gap-4 lg:grid-cols-2" onSubmit={submit}>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Tipo pago</span>
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.tipoPago} onChange={(e) => setForm((c) => ({ ...c, tipoPago: e.target.value }))} data-testid="payment-form-tipoPago-select">{PAYMENT_TYPES.map((option) => <option key={option} value={option}>{option}</option>)}</select>
          </label>
          <label>
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Fase</span>
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.faseId} onChange={(e) => setForm((c) => ({ ...c, faseId: e.target.value }))} data-testid="payment-form-faseId-select">{project.fases.map((fase) => <option key={fase.id} value={fase.id}>{fase.nombre}</option>)}</select>
          </label>
          <Input type="date" value={form.fechaPago} onChange={(e) => setForm((c) => ({ ...c, fechaPago: e.target.value }))} data-testid="payment-form-date-input" />
          <Input type="number" value={form.monto} onChange={(e) => setForm((c) => ({ ...c, monto: e.target.value }))} data-testid="payment-form-amount-input" />
          <Input type="text" value={form.metodoPago} onChange={(e) => setForm((c) => ({ ...c, metodoPago: e.target.value }))} data-testid="payment-form-method-input" />
          <Input type="text" value={form.referencia} onChange={(e) => setForm((c) => ({ ...c, referencia: e.target.value }))} data-testid="payment-form-reference-input" />
          <Input type="text" className="lg:col-span-2" value={form.concepto} onChange={(e) => setForm((c) => ({ ...c, concepto: e.target.value }))} data-testid="payment-form-concept-input" />
          <Textarea className="lg:col-span-2" value={form.observaciones} onChange={(e) => setForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="payment-form-observations-input" />
          <div className="lg:col-span-2 flex justify-end gap-2">
            {editingId ? <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={reset} data-testid="payment-form-cancel-button"><X className="h-4 w-4" /> Cancelar</Button> : null}
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="payment-form-submit-button">{editingId ? "Actualizar pago" : "Registrar pago"}</Button>
          </div>
        </form>
      </SectionCard>

      <div className="mt-6 grid gap-4">
        {project.pagos.map((payment) => (
          <div key={payment.idPago} className="rounded-sm border border-zinc-200 bg-white p-4" data-testid={`payment-card-${payment.idPago}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <StatusBadge value={payment.tipoPago} testId={`payment-card-badge-${payment.idPago}`} />
                <p className="mt-3 text-lg font-semibold text-zinc-950">{formatCurrency(payment.monto)}</p>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startEdit(payment)} data-testid={`payment-edit-button-${payment.idPago}`}><Pencil className="h-4 w-4" /></Button>
                <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => onRequestDelete({ endpoint: `/proyectos/${project.id}/pagos/${payment.idPago}`, label: `Pago ${payment.concepto || payment.idPago}`, type: "Pago" })} data-testid={`payment-delete-button-${payment.idPago}`}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap justify-between gap-3 text-sm text-zinc-600">
              <span>{formatDate(payment.fechaPago)}</span>
              <span>{payment.metodoPago}</span>
            </div>
            <p className="mt-3 text-sm text-zinc-700">{payment.concepto}</p>
          </div>
        ))}
      </div>
    </>
  );
}
