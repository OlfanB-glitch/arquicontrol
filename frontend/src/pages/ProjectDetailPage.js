import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, FileSpreadsheet, FileText, Pencil, Trash2, X } from "lucide-react";

import { LogicalDeleteDialog } from "@/components/forms/LogicalDeleteDialog";
import { AuditTab, ContractorsTab, DocumentsTab, PaymentsTab, PurchasesTab, TrackingTab } from "@/components/project-detail";
import { MetricCard } from "@/components/shared/MetricCard";
import { PageHeader } from "@/components/shared/PageHeader";
import { SectionCard } from "@/components/shared/SectionCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import api, { downloadApiFile } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

const initialPhaseForm = {
  nombre: "", descripcion: "", porcentajePlaneado: 0, porcentajeAvance: 0,
  fechaInicio: "", fechaFinEstimada: "", estado: "PENDIENTE",
};

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [clients, setClients] = useState([]);
  const [contractors, setContractors] = useState([]);
  const [providers, setProviders] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [phaseForm, setPhaseForm] = useState(initialPhaseForm);
  const [editingPhaseId, setEditingPhaseId] = useState("");
  const [logicalDeleteTarget, setLogicalDeleteTarget] = useState(null);
  const [isLogicalDeleteOpen, setIsLogicalDeleteOpen] = useState(false);
  const [isDeleteSubmitting, setIsDeleteSubmitting] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState("");

  async function loadData() {
    const [projectRes, clientsRes, contractorsRes, providersRes, materialsRes] = await Promise.all([
      api.get(`/proyectos/${projectId}`),
      api.get("/clientes"),
      api.get("/contratistas"),
      api.get("/proveedores"),
      api.get("/materiales"),
    ]);
    setProject(projectRes.data);
    setClients(clientsRes.data);
    setContractors(contractorsRes.data);
    setProviders(providersRes.data);
    setMaterials(materialsRes.data);
  }

  useEffect(() => { loadData(); }, [projectId]);

  const clientMap = useMemo(() => Object.fromEntries(clients.map((c) => [c.id, c.nombreCompleto])), [clients]);
  const contractorMap = useMemo(() => Object.fromEntries(contractors.map((c) => [c.id, c.nombreCompleto])), [contractors]);
  const providerMap = useMemo(() => Object.fromEntries(providers.map((p) => [p.id, p.nombre])), [providers]);
  const materialMap = useMemo(() => Object.fromEntries(materials.map((m) => [m.id, m.nombre])), [materials]);

  if (!project) {
    return <div className="rounded-sm border border-zinc-200 bg-white p-8 text-sm text-zinc-600" data-testid="project-detail-loading">Cargando detalle del proyecto...</div>;
  }

  function handleRequestError(error) {
    toast.error(error.response?.data?.detail || "No fue posible completar la operación.");
  }

  function openLogicalDeleteDialog(target) {
    setLogicalDeleteTarget(target);
    setIsLogicalDeleteOpen(true);
  }

  async function confirmLogicalDelete(motivo) {
    if (!logicalDeleteTarget?.endpoint) return;
    setIsDeleteSubmitting(true);
    try {
      const response = await api.delete(logicalDeleteTarget.endpoint, { data: { motivo } });
      setProject(response.data);
      setIsLogicalDeleteOpen(false);
      setLogicalDeleteTarget(null);
      toast.success("La baja lógica se registró y quedó trazada en bitácora.");
    } catch (error) {
      handleRequestError(error);
    } finally {
      setIsDeleteSubmitting(false);
    }
  }

  async function handleReportDownload(type, endpoint, fallbackName) {
    setDownloadingReport(type);
    try {
      await downloadApiFile(endpoint, fallbackName);
      toast.success("El reporte se generó correctamente.");
    } catch (error) {
      handleRequestError(error);
    } finally {
      setDownloadingReport("");
    }
  }

  function resetPhaseEditor() {
    setEditingPhaseId("");
    setPhaseForm(initialPhaseForm);
  }

  function startPhaseEdit(phase) {
    setEditingPhaseId(phase.id);
    setPhaseForm({ nombre: phase.nombre, descripcion: phase.descripcion, porcentajePlaneado: phase.porcentajePlaneado, porcentajeAvance: phase.porcentajeAvance, fechaInicio: phase.fechaInicio || "", fechaFinEstimada: phase.fechaFinEstimada || "", estado: phase.estado });
  }

  async function submitPhase(event) {
    event.preventDefault();
    if (!editingPhaseId) return;
    try {
      const response = await api.put(`/proyectos/${project.id}/fases/${editingPhaseId}`, { ...phaseForm, porcentajePlaneado: Number(phaseForm.porcentajePlaneado || 0), porcentajeAvance: Number(phaseForm.porcentajeAvance || 0) });
      setProject(response.data);
      resetPhaseEditor();
    } catch (error) {
      handleRequestError(error);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        kicker="Detalle operativo"
        title={project.nombreProyecto}
        description={`Cliente: ${clientMap[project.clienteId] || "Sin cliente"} · Código ${project.codigoProyecto} · Ubicación ${project.ubicacion}`}
        actions={<Link to="/proyectos" className="inline-flex items-center gap-2 rounded-sm border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-100" data-testid="project-detail-back-link"><ArrowLeft className="h-4 w-4" /> Volver a proyectos</Link>}
      />

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Contrato" value={formatCurrency(project.valorContrato)} detail="Valor contractual vigente" color="blue" testId="project-detail-metric-contract" />
        <MetricCard title="Pagado cliente" value={formatCurrency(project.resumenFinanciero?.totalPagadoCliente)} detail="Cobros recibidos a la fecha" color="green" testId="project-detail-metric-paid" />
        <MetricCard title="Saldo pendiente" value={formatCurrency(project.resumenFinanciero?.saldoPendienteCliente)} detail="Restricción para cierre del proyecto" color={project.resumenFinanciero?.saldoPendienteCliente > 0 ? "amber" : "green"} testId="project-detail-metric-pending" />
        <MetricCard title="Avance general" value={`${project.porcentajeAvanceGeneral}%`} detail="Calculado por estrategia activa" color={project.porcentajeAvanceGeneral >= 80 ? "green" : project.porcentajeAvanceGeneral >= 50 ? "blue" : "amber"} testId="project-detail-metric-progress" />
      </div>

      <SectionCard title="Resumen técnico" description="Datos generales, fases activas y observaciones maestras del proyecto." testId="project-detail-summary-card" accent="teal">
        <div className="grid gap-6 xl:grid-cols-[1.1fr_1fr]">
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-sm border border-zinc-200 p-4" data-testid="project-detail-general-state">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Estado proyecto</p>
                <div className="mt-3"><StatusBadge value={project.estadoProyecto} testId="project-detail-status-badge" /></div>
              </div>
              <div className="rounded-sm border border-zinc-200 p-4" data-testid="project-detail-general-area">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Área registrada</p>
                <p className="mt-3 text-lg font-semibold text-zinc-950">{project.area?.valor} {project.area?.unidad}</p>
                <p className="mt-1 text-sm text-zinc-600">{project.area?.tipoArea}</p>
              </div>
            </div>
            <div className="rounded-sm border border-zinc-200 p-4" data-testid="project-detail-observations-box">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Observaciones generales</p>
              <p className="mt-3 text-sm text-zinc-700">{project.observacionesGenerales || "Sin observaciones"}</p>
            </div>

            {editingPhaseId ? (
              <form className="grid gap-3 rounded-sm border border-zinc-200 p-4 md:grid-cols-2" onSubmit={submitPhase} data-testid="phase-edit-form">
                <Input value={phaseForm.nombre} onChange={(e) => setPhaseForm((c) => ({ ...c, nombre: e.target.value }))} data-testid="phase-form-name-input" />
                <Input value={phaseForm.estado} onChange={(e) => setPhaseForm((c) => ({ ...c, estado: e.target.value }))} data-testid="phase-form-status-input" />
                <Input type="number" value={phaseForm.porcentajePlaneado} onChange={(e) => setPhaseForm((c) => ({ ...c, porcentajePlaneado: e.target.value }))} data-testid="phase-form-planned-input" />
                <Input type="number" value={phaseForm.porcentajeAvance} onChange={(e) => setPhaseForm((c) => ({ ...c, porcentajeAvance: e.target.value }))} data-testid="phase-form-progress-input" />
                <Input type="date" value={phaseForm.fechaInicio} onChange={(e) => setPhaseForm((c) => ({ ...c, fechaInicio: e.target.value }))} data-testid="phase-form-start-input" />
                <Input type="date" value={phaseForm.fechaFinEstimada} onChange={(e) => setPhaseForm((c) => ({ ...c, fechaFinEstimada: e.target.value }))} data-testid="phase-form-end-input" />
                <Textarea className="md:col-span-2" value={phaseForm.descripcion} onChange={(e) => setPhaseForm((c) => ({ ...c, descripcion: e.target.value }))} data-testid="phase-form-description-input" />
                <div className="md:col-span-2 flex justify-end gap-2">
                  <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={resetPhaseEditor} data-testid="phase-form-cancel-button"><X className="h-4 w-4" /> Cancelar</Button>
                  <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="phase-form-submit-button">Actualizar fase</Button>
                </div>
              </form>
            ) : null}
          </div>

          <div className="space-y-3">
            {project.fases.map((fase) => (
              <div key={fase.id} className="rounded-sm border border-zinc-200 p-4" data-testid={`project-phase-card-${fase.id}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Fase</p>
                    <h3 className="mt-2 text-base font-semibold text-zinc-950">{fase.nombre}</h3>
                  </div>
                  <div className="flex gap-2">
                    <Button type="button" variant="ghost" className="rounded-sm text-zinc-700 hover:bg-zinc-100" onClick={() => startPhaseEdit(fase)} data-testid={`phase-edit-button-${fase.id}`}><Pencil className="h-4 w-4" /></Button>
                    <Button type="button" variant="ghost" className="rounded-sm text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => openLogicalDeleteDialog({ endpoint: `/proyectos/${project.id}/fases/${fase.id}`, label: `Fase ${fase.nombre}`, type: "Fase" })} data-testid={`phase-delete-button-${fase.id}`}><Trash2 className="h-4 w-4" /></Button>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between gap-3">
                  <StatusBadge value={fase.estado} testId={`phase-status-${fase.id}`} />
                  <span className="text-sm font-medium text-zinc-700">{fase.porcentajeAvance}%</span>
                </div>
                <p className="mt-3 text-sm text-zinc-600">{fase.descripcion}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Reportes y exportaciones" description="Acciones básicas para cierre operativo y comunicación con cliente o red de contratistas." testId="project-detail-reports-card" accent="purple" actions={<div className="rounded-sm border border-zinc-200 bg-zinc-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500" data-testid="project-detail-reports-project-chip">{project.codigoProyecto}</div>}>
        <div className="grid gap-4 lg:grid-cols-3">
          <button type="button" className="flex min-h-[120px] flex-col items-start justify-between rounded-sm border border-zinc-200 bg-white p-5 text-left transition-colors duration-200 hover:border-zinc-900 hover:bg-zinc-50" onClick={() => handleReportDownload("cliente", `/proyectos/${project.id}/reportes/resumen-cliente.pdf`, `${project.codigoProyecto}-resumen-cliente.pdf`)} data-testid="project-report-client-summary-button">
            <FileText className="h-5 w-5 text-zinc-900" />
            <div><p className="text-sm font-semibold text-zinc-950">PDF resumen para cliente</p><p className="mt-2 text-sm text-zinc-600">Incluye estado, avance, corte financiero y hitos recientes del proyecto.</p></div>
            <span className="text-xs uppercase tracking-[0.12em] text-zinc-500">{downloadingReport === "cliente" ? "Generando..." : "Descargar PDF"}</span>
          </button>
          <button type="button" className="flex min-h-[120px] flex-col items-start justify-between rounded-sm border border-zinc-200 bg-white p-5 text-left transition-colors duration-200 hover:border-zinc-900 hover:bg-zinc-50" onClick={() => handleReportDownload("finanzas", `/proyectos/${project.id}/reportes/pagos-compras.csv`, `${project.codigoProyecto}-pagos-compras.csv`)} data-testid="project-report-payments-purchases-button">
            <FileSpreadsheet className="h-5 w-5 text-zinc-900" />
            <div><p className="text-sm font-semibold text-zinc-950">CSV de pagos y compras</p><p className="mt-2 text-sm text-zinc-600">Consolida pagos de cliente y compras del proyecto en una sola exportación.</p></div>
            <span className="text-xs uppercase tracking-[0.12em] text-zinc-500">{downloadingReport === "finanzas" ? "Generando..." : "Descargar CSV"}</span>
          </button>
          <button type="button" className="flex min-h-[120px] flex-col items-start justify-between rounded-sm border border-zinc-200 bg-white p-5 text-left transition-colors duration-200 hover:border-zinc-900 hover:bg-zinc-50" onClick={() => handleReportDownload("contratistas", `/proyectos/${project.id}/reportes/contratistas.csv`, `${project.codigoProyecto}-pagos-contratistas.csv`)} data-testid="project-report-contractor-payments-button">
            <FileSpreadsheet className="h-5 w-5 text-zinc-900" />
            <div><p className="text-sm font-semibold text-zinc-950">CSV de pagos a contratistas</p><p className="mt-2 text-sm text-zinc-600">Entrega un corte claro por contratista, rol, estado de asignación y desembolsos.</p></div>
            <span className="text-xs uppercase tracking-[0.12em] text-zinc-500">{downloadingReport === "contratistas" ? "Generando..." : "Descargar CSV"}</span>
          </button>
        </div>
      </SectionCard>

      <Tabs defaultValue="seguimientos" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 rounded-sm bg-zinc-100 p-1 lg:grid-cols-6">
          {[["seguimientos", "Seguimientos"], ["pagos", "Pagos"], ["contratistas", "Contratistas"], ["compras", "Compras"], ["documentos", "Documentos"], ["auditoria", "Auditoría"]].map(([value, label]) => (
            <TabsTrigger key={value} value={value} className="rounded-sm data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 data-[state=active]:shadow-none" data-testid={`project-tab-${value}`}>{label}</TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="seguimientos">
          <TrackingTab project={project} setProject={setProject} onRequestDelete={openLogicalDeleteDialog} />
        </TabsContent>
        <TabsContent value="pagos">
          <PaymentsTab project={project} setProject={setProject} onRequestDelete={openLogicalDeleteDialog} />
        </TabsContent>
        <TabsContent value="contratistas">
          <ContractorsTab project={project} setProject={setProject} contractors={contractors} contractorMap={contractorMap} onRequestDelete={openLogicalDeleteDialog} />
        </TabsContent>
        <TabsContent value="compras">
          <PurchasesTab project={project} setProject={setProject} providers={providers} materials={materials} providerMap={providerMap} materialMap={materialMap} onRequestDelete={openLogicalDeleteDialog} />
        </TabsContent>
        <TabsContent value="documentos">
          <DocumentsTab project={project} setProject={setProject} onRequestDelete={openLogicalDeleteDialog} />
        </TabsContent>
        <TabsContent value="auditoria">
          <AuditTab project={project} />
        </TabsContent>
      </Tabs>

      <LogicalDeleteDialog open={isLogicalDeleteOpen} onOpenChange={(open) => { setIsLogicalDeleteOpen(open); if (!open) setLogicalDeleteTarget(null); }} target={logicalDeleteTarget} onConfirm={confirmLogicalDelete} isSubmitting={isDeleteSubmitting} />
    </div>
  );
}