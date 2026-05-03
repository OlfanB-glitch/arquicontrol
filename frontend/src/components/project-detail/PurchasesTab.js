import { useState } from "react";
import { Pencil, Trash2, X } from "lucide-react";

import { SectionCard } from "@/components/shared/SectionCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

const initialForm = { proveedorId: "", fechaCompra: "", numeroFactura: "", impuesto: 0, observaciones: "", detalleCompra: [{ materialId: "", cantidad: 1, precioUnitario: 0 }] };

export function PurchasesTab({ project, setProject, providers, materials, providerMap, materialMap, onRequestDelete }) {
  const [form, setForm] = useState({ ...initialForm, proveedorId: providers[0]?.id || "", detalleCompra: [{ materialId: materials[0]?.id || "", cantidad: 1, precioUnitario: 0 }] });
  const [editingId, setEditingId] = useState("");

  function reset() {
    setEditingId("");
    setForm({ ...initialForm, proveedorId: providers[0]?.id || "", detalleCompra: [{ materialId: materials[0]?.id || "", cantidad: 1, precioUnitario: 0 }] });
  }

  function startEdit(purchase) {
    setEditingId(purchase.idCompra);
    setForm({ proveedorId: purchase.proveedorId, fechaCompra: purchase.fechaCompra, numeroFactura: purchase.numeroFactura, impuesto: purchase.impuesto, observaciones: purchase.observaciones, detalleCompra: purchase.detalleCompra.map((d) => ({ materialId: d.materialId, cantidad: d.cantidad, precioUnitario: d.precioUnitario })) });
  }

  function updateDetail(index, field, value) {
    setForm((c) => ({ ...c, detalleCompra: c.detalleCompra.map((d, i) => (i === index ? { ...d, [field]: value } : d)) }));
  }

  async function submit(event) {
    event.preventDefault();
    const payload = { ...form, impuesto: Number(form.impuesto || 0), detalleCompra: form.detalleCompra.map((d) => ({ ...d, cantidad: Number(d.cantidad || 0), precioUnitario: Number(d.precioUnitario || 0) })) };
    try {
      const response = editingId ? await api.put(`/proyectos/${project.id}/compras/${editingId}`, payload) : await api.post(`/proyectos/${project.id}/compras`, payload);
      setProject(response.data);
      reset();
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  return (
    <>
      <SectionCard title={editingId ? "Editar compra" : "Registrar compra"} description="Cada compra debe tener al menos un detalle con material, cantidad y precio unitario." testId="project-purchases-card">
        <form className="space-y-4" onSubmit={submit}>
          <div className="grid gap-4 lg:grid-cols-2">
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={form.proveedorId} onChange={(e) => setForm((c) => ({ ...c, proveedorId: e.target.value }))} data-testid="purchase-form-provider-select">{providers.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}</select>
            <Input type="date" value={form.fechaCompra} onChange={(e) => setForm((c) => ({ ...c, fechaCompra: e.target.value }))} data-testid="purchase-form-date-input" />
            <Input type="text" placeholder="Número factura" value={form.numeroFactura} onChange={(e) => setForm((c) => ({ ...c, numeroFactura: e.target.value }))} data-testid="purchase-form-invoice-input" />
            <Input type="number" placeholder="Impuesto" value={form.impuesto} onChange={(e) => setForm((c) => ({ ...c, impuesto: e.target.value }))} data-testid="purchase-form-tax-input" />
          </div>
          <Textarea value={form.observaciones} onChange={(e) => setForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="purchase-form-observations-input" />
          <div className="space-y-3 rounded-sm border border-zinc-200 p-4">
            {form.detalleCompra.map((detail, index) => (
              <div key={`${detail.materialId}-${index}`} className="grid gap-3 md:grid-cols-[1.2fr_120px_140px_auto]" data-testid={`purchase-detail-row-${index}`}>
                <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={detail.materialId} onChange={(e) => updateDetail(index, "materialId", e.target.value)} data-testid={`purchase-detail-material-${index}`}>{materials.map((m) => <option key={m.id} value={m.id}>{m.nombre}</option>)}</select>
                <Input type="number" value={detail.cantidad} onChange={(e) => updateDetail(index, "cantidad", e.target.value)} data-testid={`purchase-detail-quantity-${index}`} />
                <Input type="number" value={detail.precioUnitario} onChange={(e) => updateDetail(index, "precioUnitario", e.target.value)} data-testid={`purchase-detail-price-${index}`} />
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => setForm((c) => ({ ...c, detalleCompra: c.detalleCompra.filter((_, i) => i !== index) }))} data-testid={`purchase-detail-remove-${index}`}>Quitar</Button>
              </div>
            ))}
            <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => setForm((c) => ({ ...c, detalleCompra: [...c.detalleCompra, { materialId: materials[0]?.id || "", cantidad: 1, precioUnitario: 0 }] }))} data-testid="purchase-form-add-detail-button">Agregar detalle</Button>
          </div>
          <div className="flex justify-end gap-2">
            {editingId ? <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={reset} data-testid="purchase-form-cancel-button"><X className="h-4 w-4" /> Cancelar</Button> : null}
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="purchase-form-submit-button">{editingId ? "Actualizar compra" : "Registrar compra"}</Button>
          </div>
        </form>
      </SectionCard>

      <div className="mt-6 space-y-4">
        {project.compras.map((purchase) => (
          <div key={purchase.idCompra} className="rounded-sm border border-zinc-200 bg-white p-5" data-testid={`purchase-card-${purchase.idCompra}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">{providerMap[purchase.proveedorId]}</p>
                <h3 className="mt-2 text-lg font-semibold text-zinc-950">Factura {purchase.numeroFactura}</h3>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startEdit(purchase)} data-testid={`purchase-edit-button-${purchase.idCompra}`}><Pencil className="h-4 w-4" /></Button>
                <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => onRequestDelete({ endpoint: `/proyectos/${project.id}/compras/${purchase.idCompra}`, label: `Compra ${purchase.numeroFactura || purchase.idCompra}`, type: "Compra" })} data-testid={`purchase-delete-button-${purchase.idCompra}`}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </div>
            <p className="mt-3 text-lg font-semibold text-zinc-950">{formatCurrency(purchase.total)}</p>
            <div className="mt-4 flex flex-wrap gap-3 text-sm text-zinc-700">{purchase.detalleCompra.map((d) => <span key={d.idDetalle} className="rounded-sm border border-zinc-200 px-3 py-2" data-testid={`purchase-detail-chip-${d.idDetalle}`}>{materialMap[d.materialId]} · {d.cantidad}</span>)}</div>
          </div>
        ))}
      </div>
    </>
  );
}
