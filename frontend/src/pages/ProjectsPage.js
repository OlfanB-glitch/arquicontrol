import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";

import { ProjectFormDialog } from "@/components/forms/ProjectFormDialog";
import { FilterBar } from "@/components/shared/FilterBar";
import { MetricCard } from "@/components/shared/MetricCard";
import { ModuleTable } from "@/components/shared/ModuleTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import { buildQueryString, formatCurrency } from "@/lib/utils";

const baseFilters = {
  q: "",
  estado: "",
  clienteId: "",
  fechaDesde: "",
  fechaHasta: "",
  montoMin: "",
  montoMax: "",
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [editingProject, setEditingProject] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [draftFilters, setDraftFilters] = useState(baseFilters);
  const [filters, setFilters] = useState(baseFilters);

  async function loadData(activeFilters = filters) {
    const query = buildQueryString(activeFilters);
    const [projectsResponse, clientsResponse] = await Promise.all([
      api.get(`/proyectos${query}`),
      api.get("/clientes"),
    ]);
    setProjects(projectsResponse.data);
    setClients(clientsResponse.data);
  }

  useEffect(() => {
    loadData(filters);
  }, [filters]);

  const clientMap = useMemo(
    () => Object.fromEntries(clients.map((client) => [client.id, client.nombreCompleto])),
    [clients],
  );

  async function handleSubmit(payload) {
    setIsSubmitting(true);
    try {
      if (editingProject) {
        await api.put(`/proyectos/${editingProject.id}`, payload);
      } else {
        await api.post("/proyectos", payload);
      }
      setIsDialogOpen(false);
      setEditingProject(null);
      await loadData();
    } finally {
      setIsSubmitting(false);
    }
  }

  const totalBalance = projects.reduce((accumulator, project) => accumulator + Number(project.resumenFinanciero?.saldoPendienteCliente || 0), 0);

  return (
    <div className="space-y-8">
      <PageHeader
        kicker="Agregado raíz"
        title="Proyectos"
        description="Cada proyecto concentra fases, seguimientos, pagos, compras, documentos y asignaciones de contratistas bajo un modelo documental coherente."
        actions={(
          <Button className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" onClick={() => setIsDialogOpen(true)} data-testid="create-project-button">
            <Plus className="h-4 w-4" /> Nuevo proyecto
          </Button>
        )}
      />

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Total proyectos" value={projects.length} detail="Portafolio administrado" testId="projects-metric-total" />
        <MetricCard title="En curso" value={projects.filter((project) => ["EN_DISENO", "EN_EJECUCION"].includes(project.estadoProyecto)).length} detail="Proyectos con operación activa" testId="projects-metric-active" />
        <MetricCard title="Saldo pendiente" value={formatCurrency(totalBalance)} detail="Cobro restante del portafolio" testId="projects-metric-balance" />
        <MetricCard title="Avance promedio" value={`${Math.round(projects.reduce((accumulator, project) => accumulator + Number(project.porcentajeAvanceGeneral || 0), 0) / (projects.length || 1))}%`} detail="Indicador consolidado" testId="projects-metric-progress" />
      </div>

      <FilterBar
        filters={draftFilters}
        setFilters={setDraftFilters}
        clients={clients}
        amountLabel="Contrato"
        onApply={() => setFilters({ ...draftFilters })}
        onReset={() => {
          setDraftFilters(baseFilters);
          setFilters(baseFilters);
        }}
      />

      <ModuleTable
        items={projects}
        onEdit={(project) => { setEditingProject(project); setIsDialogOpen(true); }}
        columns={[
          { key: "codigoProyecto", label: "Código" },
          { key: "nombreProyecto", label: "Proyecto", render: (project) => <Link className="font-semibold text-zinc-950 underline-offset-4 hover:underline" to={`/proyectos/${project.id}`} data-testid={`project-detail-link-${project.id}`}>{project.nombreProyecto}</Link> },
          { key: "clienteId", label: "Cliente", render: (project) => clientMap[project.clienteId] || "—" },
          { key: "estadoProyecto", label: "Estado", render: (project) => <StatusBadge value={project.estadoProyecto} testId={`project-status-${project.id}`} /> },
          { key: "valorContrato", label: "Contrato", render: (project) => formatCurrency(project.valorContrato) },
          { key: "resumenFinanciero.saldoPendienteCliente", label: "Saldo", render: (project) => formatCurrency(project.resumenFinanciero?.saldoPendienteCliente) },
          { key: "porcentajeAvanceGeneral", label: "Avance", render: (project) => `${project.porcentajeAvanceGeneral}%` },
        ]}
        emptyMessage="Aún no has registrado proyectos en ArquiControl."
      />

      <ProjectFormDialog
        open={isDialogOpen}
        onOpenChange={(value) => {
          setIsDialogOpen(value);
          if (!value) setEditingProject(null);
        }}
        clients={clients}
        initialValues={editingProject}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}