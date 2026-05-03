import { useEffect, useMemo, useState } from "react";
import { Plus } from "lucide-react";

import { EntityFormDialog } from "@/components/forms/EntityFormDialog";
import { MetricCard } from "@/components/shared/MetricCard";
import { ModuleTable } from "@/components/shared/ModuleTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

function getColumns(moduleKey) {
  if (moduleKey === "clientes") {
    return [
      { key: "numeroDocumento", label: "Documento" },
      { key: "nombreCompleto", label: "Cliente" },
      { key: "ciudad", label: "Ciudad" },
      { key: "correo", label: "Correo" },
      { key: "estado", label: "Estado", render: (item) => <StatusBadge value={item.estado} testId={`entity-status-${item.id}`} /> },
    ];
  }
  if (moduleKey === "contratistas") {
    return [
      { key: "nombreCompleto", label: "Contratista" },
      { key: "especialidad", label: "Especialidad" },
      { key: "tarifaBase", label: "Tarifa base", render: (item) => formatCurrency(item.tarifaBase) },
      { key: "correo", label: "Correo" },
      { key: "estado", label: "Estado", render: (item) => <StatusBadge value={item.estado} testId={`entity-status-${item.id}`} /> },
    ];
  }
  if (moduleKey === "proveedores") {
    return [
      { key: "nit", label: "NIT" },
      { key: "nombre", label: "Proveedor" },
      { key: "contactoPrincipal", label: "Contacto" },
      { key: "correo", label: "Correo" },
      { key: "estado", label: "Estado", render: (item) => <StatusBadge value={item.estado} testId={`entity-status-${item.id}`} /> },
    ];
  }
  return [
    { key: "codigoMaterial", label: "Código" },
    { key: "nombre", label: "Material" },
    { key: "unidadMedida", label: "Unidad" },
    { key: "precioReferencia", label: "Precio", render: (item) => formatCurrency(item.precioReferencia) },
    { key: "estado", label: "Estado", render: (item) => <StatusBadge value={item.estado} testId={`entity-status-${item.id}`} /> },
  ];
}

export default function EntityPage({ moduleKey, config }) {
  const [items, setItems] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  async function loadItems() {
    const response = await api.get(config.endpoint);
    setItems(response.data);
  }

  useEffect(() => {
    loadItems();
  }, [config.endpoint]);

  const columns = useMemo(() => getColumns(moduleKey), [moduleKey]);

  async function handleSubmit(payload) {
    setIsSubmitting(true);
    try {
      if (editingItem) {
        await api.put(`${config.endpoint}/${editingItem.id}`, payload);
      } else {
        await api.post(config.endpoint, payload);
      }
      setIsDialogOpen(false);
      setEditingItem(null);
      await loadItems();
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        kicker={`Gestión de ${config.title.toLowerCase()}`}
        title={config.title}
        description={config.description}
        actions={(
          <Button className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" onClick={() => setIsDialogOpen(true)} data-testid={`create-${moduleKey}-button`}>
            <Plus className="h-4 w-4" /> Nuevo {config.singular}
          </Button>
        )}
      />

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <MetricCard title="Total" value={items.length} detail={`Registros de ${config.title.toLowerCase()}`} testId={`${moduleKey}-metric-total`} />
        <MetricCard title="Activos" value={items.filter((item) => item.estado === "ACTIVO").length} detail="Disponibles para nuevas operaciones" testId={`${moduleKey}-metric-active`} />
        <MetricCard title="Cobertura" value={`${Math.round((items.filter((item) => item.estado === "ACTIVO").length / (items.length || 1)) * 100)}%`} detail="Proporción de registros activos" testId={`${moduleKey}-metric-coverage`} />
      </div>

      <ModuleTable columns={columns} items={items} onEdit={(item) => { setEditingItem(item); setIsDialogOpen(true); }} emptyMessage={`Aún no hay ${config.title.toLowerCase()} cargados.`} />

      <EntityFormDialog
        open={isDialogOpen}
        onOpenChange={(value) => {
          setIsDialogOpen(value);
          if (!value) setEditingItem(null);
        }}
        title={editingItem ? `Editar ${config.singular}` : `Nuevo ${config.singular}`}
        description={`Completa la ficha de ${config.singular} con datos consistentes para el estudio.`}
        fields={config.fields}
        initialValues={editingItem}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}