import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { PROJECT_STATUSES, PROJECT_TYPES } from "@/lib/catalogs";

const baseProject = {
  codigoProyecto: "",
  clienteId: "",
  nombreProyecto: "",
  tipoProyecto: PROJECT_TYPES[0],
  descripcion: "",
  ubicacion: "",
  areaValor: "",
  areaUnidad: "m2",
  areaTipoArea: "Construida",
  presupuestoEstimado: "",
  valorContrato: "",
  estadoProyecto: PROJECT_STATUSES[0],
  fechaInicio: "",
  fechaFinEstimada: "",
  observacionesGenerales: "",
  metodoCalculoAvance: "SEGUIMIENTOS",
};

export function ProjectFormDialog({ open, onOpenChange, clients, initialValues, onSubmit, isSubmitting }) {
  const [formState, setFormState] = useState(baseProject);
  const [phases, setPhases] = useState([{ nombre: "", descripcion: "", porcentajePlaneado: 0 }]);
  const [error, setError] = useState("");

  const normalizedValues = useMemo(() => {
    if (!initialValues) return null;
    return {
      ...initialValues,
      areaValor: initialValues.area?.valor || "",
      areaUnidad: initialValues.area?.unidad || "m2",
      areaTipoArea: initialValues.area?.tipoArea || "Construida",
    };
  }, [initialValues]);

  useEffect(() => {
    if (normalizedValues) {
      setFormState({ ...baseProject, ...normalizedValues });
      setPhases(
        normalizedValues.fases?.length
          ? normalizedValues.fases.map((phase) => ({
              nombre: phase.nombre,
              descripcion: phase.descripcion,
              porcentajePlaneado: phase.porcentajePlaneado,
            }))
          : [{ nombre: "", descripcion: "", porcentajePlaneado: 0 }],
      );
    } else {
      setFormState({ ...baseProject, clienteId: clients[0]?.id || "" });
      setPhases([{ nombre: "", descripcion: "", porcentajePlaneado: 0 }]);
    }
    setError("");
  }, [clients, normalizedValues, open]);

  function updatePhase(index, field, value) {
    setPhases((current) => current.map((phase, currentIndex) => (currentIndex === index ? { ...phase, [field]: value } : phase)));
  }

  async function handleSave(event) {
    event.preventDefault();
    if (!formState.codigoProyecto || !formState.clienteId || !formState.nombreProyecto) {
      setError("Código, cliente y nombre del proyecto son obligatorios.");
      return;
    }
    if (!phases.every((phase) => phase.nombre)) {
      setError("Cada fase debe tener al menos un nombre.");
      return;
    }

    setError("");
    await onSubmit({
      codigoProyecto: formState.codigoProyecto,
      clienteId: formState.clienteId,
      nombreProyecto: formState.nombreProyecto,
      tipoProyecto: formState.tipoProyecto,
      descripcion: formState.descripcion,
      ubicacion: formState.ubicacion,
      area: {
        valor: Number(formState.areaValor || 0),
        unidad: formState.areaUnidad,
        tipoArea: formState.areaTipoArea,
      },
      presupuestoEstimado: Number(formState.presupuestoEstimado || 0),
      valorContrato: Number(formState.valorContrato || 0),
      estadoProyecto: formState.estadoProyecto,
      fechaInicio: formState.fechaInicio,
      fechaFinEstimada: formState.fechaFinEstimada,
      porcentajeAvanceGeneral: Number(initialValues?.porcentajeAvanceGeneral || 0),
      observacionesGenerales: formState.observacionesGenerales,
      metodoCalculoAvance: formState.metodoCalculoAvance,
      fases: phases.map((phase) => ({
        nombre: phase.nombre,
        descripcion: phase.descripcion,
        porcentajePlaneado: Number(phase.porcentajePlaneado || 0),
        porcentajeAvance: 0,
        fechaInicio: formState.fechaInicio,
        fechaFinEstimada: formState.fechaFinEstimada,
        estado: "PENDIENTE",
      })),
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-5xl overflow-auto rounded-sm border-zinc-200 bg-white">
        <DialogHeader>
          <DialogTitle data-testid="project-form-dialog-title">{initialValues ? "Editar proyecto" : "Nuevo proyecto"}</DialogTitle>
          <DialogDescription data-testid="project-form-dialog-description">
            Registra datos generales, fases y criterios técnicos del proyecto.
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-6" onSubmit={handleSave}>
          <div className="grid gap-4 md:grid-cols-2">
            {[
              ["codigoProyecto", "Código proyecto", "text"],
              ["nombreProyecto", "Nombre proyecto", "text"],
              ["descripcion", "Descripción", "textarea"],
              ["ubicacion", "Ubicación", "text"],
              ["presupuestoEstimado", "Presupuesto estimado", "number"],
              ["valorContrato", "Valor contrato", "number"],
              ["fechaInicio", "Fecha inicio", "date"],
              ["fechaFinEstimada", "Fecha fin estimada", "date"],
              ["observacionesGenerales", "Observaciones generales", "textarea"],
            ].map(([name, label, type]) => (
              <label key={name} className={type === "textarea" ? "md:col-span-2" : "block"}>
                <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">{label}</span>
                {type === "textarea" ? (
                  <Textarea className="min-h-[120px] rounded-sm border-zinc-300" value={formState[name]} onChange={(event) => setFormState((current) => ({ ...current, [name]: event.target.value }))} data-testid={`project-form-field-${name}`} />
                ) : (
                  <Input type={type} className="rounded-sm border-zinc-300" value={formState[name]} onChange={(event) => setFormState((current) => ({ ...current, [name]: event.target.value }))} data-testid={`project-form-field-${name}`} />
                )}
              </label>
            ))}

            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Cliente</span>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={formState.clienteId} onChange={(event) => setFormState((current) => ({ ...current, clienteId: event.target.value }))} data-testid="project-form-field-clienteId">
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>{client.nombreCompleto}</option>
                ))}
              </select>
            </label>

            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Tipo proyecto</span>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={formState.tipoProyecto} onChange={(event) => setFormState((current) => ({ ...current, tipoProyecto: event.target.value }))} data-testid="project-form-field-tipoProyecto">
                {PROJECT_TYPES.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </label>

            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Estado</span>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={formState.estadoProyecto} onChange={(event) => setFormState((current) => ({ ...current, estadoProyecto: event.target.value }))} data-testid="project-form-field-estadoProyecto">
                {PROJECT_STATUSES.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </label>

            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Método avance</span>
              <select className="flex h-10 w-full rounded-sm border border-zinc-300 px-3 text-sm" value={formState.metodoCalculoAvance} onChange={(event) => setFormState((current) => ({ ...current, metodoCalculoAvance: event.target.value }))} data-testid="project-form-field-metodoCalculoAvance">
                {[
                  ["SEGUIMIENTOS", "Por seguimientos"],
                  ["FASES", "Por fases"],
                ].map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>

            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Área valor</span>
              <Input type="number" className="rounded-sm border-zinc-300" value={formState.areaValor} onChange={(event) => setFormState((current) => ({ ...current, areaValor: event.target.value }))} data-testid="project-form-field-areaValor" />
            </label>
            <label>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Área unidad</span>
              <Input type="text" className="rounded-sm border-zinc-300" value={formState.areaUnidad} onChange={(event) => setFormState((current) => ({ ...current, areaUnidad: event.target.value }))} data-testid="project-form-field-areaUnidad" />
            </label>
            <label className="md:col-span-2">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Tipo de área</span>
              <Input type="text" className="rounded-sm border-zinc-300" value={formState.areaTipoArea} onChange={(event) => setFormState((current) => ({ ...current, areaTipoArea: event.target.value }))} data-testid="project-form-field-areaTipoArea" />
            </label>
          </div>

          <div className="space-y-4 rounded-sm border border-zinc-200 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Fases del proyecto</p>
                <p className="mt-1 text-sm text-zinc-600">Define el esqueleto del proyecto como agregado raíz.</p>
              </div>
              <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => setPhases((current) => [...current, { nombre: "", descripcion: "", porcentajePlaneado: 0 }])} data-testid="project-form-add-phase-button">
                Agregar fase
              </Button>
            </div>

            <div className="space-y-3">
              {phases.map((phase, index) => (
                <div key={`${phase.nombre}-${index}`} className="grid gap-3 border border-zinc-200 p-3 md:grid-cols-[1.3fr_2fr_120px_auto]" data-testid={`project-form-phase-row-${index}`}>
                  <Input type="text" placeholder="Nombre fase" className="rounded-sm border-zinc-300" value={phase.nombre} onChange={(event) => updatePhase(index, "nombre", event.target.value)} data-testid={`project-form-phase-name-${index}`} />
                  <Input type="text" placeholder="Descripción" className="rounded-sm border-zinc-300" value={phase.descripcion} onChange={(event) => updatePhase(index, "descripcion", event.target.value)} data-testid={`project-form-phase-description-${index}`} />
                  <Input type="number" placeholder="% planeado" className="rounded-sm border-zinc-300" value={phase.porcentajePlaneado} onChange={(event) => updatePhase(index, "porcentajePlaneado", event.target.value)} data-testid={`project-form-phase-progress-${index}`} />
                  <Button type="button" variant="ghost" className="rounded-sm text-zinc-600 hover:bg-zinc-100" onClick={() => setPhases((current) => current.filter((_, phaseIndex) => phaseIndex !== index))} data-testid={`project-form-remove-phase-${index}`}>
                    Quitar
                  </Button>
                </div>
              ))}
            </div>
          </div>

          {error ? <p className="text-sm text-red-600" data-testid="project-form-error-message">{error}</p> : null}

          <DialogFooter>
            <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => onOpenChange(false)} data-testid="project-form-cancel-button">
              Cancelar
            </Button>
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" disabled={isSubmitting} data-testid="project-form-submit-button">
              {isSubmitting ? "Guardando..." : "Guardar proyecto"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}