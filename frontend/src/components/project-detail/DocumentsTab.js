import { useState } from "react";
import { Link2, Pencil, Trash2, Upload, X } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { SectionCard } from "@/components/shared/SectionCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import api, { openDocumentResource } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const initialDocForm = { nombre: "", url: "", tipo: "DOCUMENTO", seguimientoId: "", observaciones: "" };

export function DocumentsTab({ project, setProject, onRequestDelete }) {
  const [docForm, setDocForm] = useState(initialDocForm);
  const [editingId, setEditingId] = useState("");
  const [uploadForm, setUploadForm] = useState({ tipo: "DOCUMENTO", seguimientoId: "", observaciones: "", file: null });

  function resetDoc() {
    setEditingId("");
    setDocForm(initialDocForm);
  }

  function startEdit(doc) {
    setEditingId(doc.id);
    setDocForm({ nombre: doc.nombre, url: doc.url, tipo: doc.tipo, seguimientoId: doc.seguimientoId || "", observaciones: doc.observaciones || "" });
  }

  async function submitDoc(event) {
    event.preventDefault();
    try {
      const payload = { ...docForm, seguimientoId: docForm.seguimientoId || null };
      const response = editingId ? await api.put(`/proyectos/${project.id}/documentos/${editingId}`, payload) : await api.post(`/proyectos/${project.id}/documentos/url`, payload);
      setProject(response.data);
      resetDoc();
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  async function submitUpload(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("tipo", uploadForm.tipo);
    formData.append("seguimientoId", uploadForm.seguimientoId || "");
    formData.append("observaciones", uploadForm.observaciones);
    formData.append("file", uploadForm.file);
    try {
      const response = await api.post(`/proyectos/${project.id}/documentos/upload`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      setProject(response.data);
      setUploadForm({ tipo: "DOCUMENTO", seguimientoId: "", observaciones: "", file: null });
    } catch (error) {
      toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
    }
  }

  return (
    <>
      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title={editingId ? "Editar documento" : "Registrar documento por URL"} description="Guarda contratos, planos o referencias externas asociadas al proyecto o a un seguimiento." testId="project-documents-url-card">
          <form className="grid gap-4" onSubmit={submitDoc}>
            <Input type="text" placeholder="Nombre" value={docForm.nombre} onChange={(e) => setDocForm((c) => ({ ...c, nombre: e.target.value }))} data-testid="document-url-name-input" />
            <Input type="text" placeholder="URL o ruta" value={docForm.url} onChange={(e) => setDocForm((c) => ({ ...c, url: e.target.value }))} data-testid="document-url-link-input" />
            <Input type="text" placeholder="Tipo" value={docForm.tipo} onChange={(e) => setDocForm((c) => ({ ...c, tipo: e.target.value }))} data-testid="document-url-type-input" />
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={docForm.seguimientoId} onChange={(e) => setDocForm((c) => ({ ...c, seguimientoId: e.target.value }))} data-testid="document-url-tracking-select">
              <option value="">Documento general del proyecto</option>
              {project.seguimientos.map((t) => <option key={t.id} value={t.id}>{t.observaciones}</option>)}
            </select>
            <Textarea value={docForm.observaciones} onChange={(e) => setDocForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="document-url-observations-input" />
            <div className="flex justify-end gap-2">
              {editingId ? <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={resetDoc} data-testid="document-url-cancel-button"><X className="h-4 w-4" /> Cancelar</Button> : null}
              <Button type="submit" variant={editingId ? "default" : "outline"} className={editingId ? "rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" : "rounded-sm border-zinc-300"} data-testid="document-url-submit-button"><Link2 className="h-4 w-4" /> {editingId ? "Actualizar documento" : "Guardar URL"}</Button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Subir archivo" description="Carga evidencia real al servidor local y guarda metadatos dentro del agregado proyecto." testId="project-documents-upload-card">
          <form className="grid gap-4" onSubmit={submitUpload}>
            <Input type="text" placeholder="Tipo archivo" value={uploadForm.tipo} onChange={(e) => setUploadForm((c) => ({ ...c, tipo: e.target.value }))} data-testid="document-upload-type-input" />
            <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={uploadForm.seguimientoId} onChange={(e) => setUploadForm((c) => ({ ...c, seguimientoId: e.target.value }))} data-testid="document-upload-tracking-select">
              <option value="">Documento general del proyecto</option>
              {project.seguimientos.map((t) => <option key={t.id} value={t.id}>{t.observaciones}</option>)}
            </select>
            <input type="file" className="rounded-sm border border-zinc-300 px-3 py-2 text-sm" onChange={(e) => setUploadForm((c) => ({ ...c, file: e.target.files?.[0] || null }))} data-testid="document-upload-file-input" />
            <Textarea value={uploadForm.observaciones} onChange={(e) => setUploadForm((c) => ({ ...c, observaciones: e.target.value }))} data-testid="document-upload-observations-input" />
            <div className="flex justify-end"><Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" disabled={!uploadForm.file} data-testid="document-upload-submit-button"><Upload className="h-4 w-4" /> Subir archivo</Button></div>
          </form>
        </SectionCard>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {project.documentos.length ? project.documentos.map((doc) => (
          <div key={doc.id} className="rounded-sm border border-zinc-200 bg-white p-5" data-testid={`project-document-card-${doc.id}`}>
            <div className="flex items-start justify-between gap-3">
              <StatusBadge value={doc.tipo} testId={`project-document-badge-${doc.id}`} />
              <div className="flex gap-2">
                <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startEdit(doc)} data-testid={`project-document-edit-button-${doc.id}`}><Pencil className="h-4 w-4" /></Button>
                <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => onRequestDelete({ endpoint: `/proyectos/${project.id}/documentos/${doc.id}`, label: `Documento ${doc.nombre}`, type: "Documento" })} data-testid={`project-document-delete-button-${doc.id}`}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </div>
            <button type="button" onClick={() => openDocumentResource(doc.url)} className="mt-4 text-left" data-testid={`project-document-link-${doc.id}`}>
              <h3 className="text-lg font-semibold text-zinc-950">{doc.nombre}</h3>
              <p className="mt-2 text-sm text-zinc-600">{doc.observaciones || "Documento asociado al proyecto"}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.12em] text-zinc-500">{formatDate(doc.fechaRegistro)}</p>
            </button>
          </div>
        )) : <EmptyState title="Sin documentos activos" description="Registra documentos por URL o carga archivos reales del proyecto." />}
      </div>
    </>
  );
}
