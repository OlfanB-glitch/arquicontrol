import { useEffect, useState } from "react";

import { EmptyState } from "@/components/shared/EmptyState";
import { FilterBar } from "@/components/shared/FilterBar";
import { ModuleTable } from "@/components/shared/ModuleTable";
import { PageHeader } from "@/components/shared/PageHeader";
import api from "@/lib/api";
import { buildQueryString } from "@/lib/utils";

const baseFilters = {
  q: "",
  estado: "",
  clienteId: "",
  fechaDesde: "",
  fechaHasta: "",
  montoMin: "",
  montoMax: "",
};

export default function FeedPage({ title, kicker, description, endpoint, columns }) {
  const [items, setItems] = useState(null);
  const [clients, setClients] = useState([]);
  const [draftFilters, setDraftFilters] = useState(baseFilters);
  const [filters, setFilters] = useState(baseFilters);

  useEffect(() => {
    async function loadFeed() {
      const query = buildQueryString(filters);
      const [itemsResponse, clientsResponse] = await Promise.all([
        api.get(`${endpoint}${query}`),
        api.get("/clientes"),
      ]);
      setItems(itemsResponse.data);
      setClients(clientsResponse.data);
    }

    loadFeed();
  }, [endpoint, filters]);

  if (!items) {
    return <div className="rounded-sm border border-zinc-200 bg-white p-8 text-sm text-zinc-600" data-testid={`feed-loading-${title.toLowerCase().replace(/\s+/g, "-")}`}>Cargando {title.toLowerCase()}...</div>;
  }

  return (
    <div className="space-y-8">
      <PageHeader kicker={kicker} title={title} description={description} />
      <FilterBar
        filters={draftFilters}
        setFilters={setDraftFilters}
        clients={clients}
        onApply={() => setFilters({ ...draftFilters })}
        onReset={() => {
          setDraftFilters(baseFilters);
          setFilters(baseFilters);
        }}
      />
      {items.length ? (
        <ModuleTable columns={columns} items={items} />
      ) : (
        <EmptyState title={`Sin ${title.toLowerCase()} todavía`} description="Los registros aparecerán aquí conforme avances en los proyectos." />
      )}
    </div>
  );
}