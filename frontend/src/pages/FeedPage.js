import { useEffect, useMemo, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";

import { EmptyState } from "@/components/shared/EmptyState";
import { FilterBar } from "@/components/shared/FilterBar";
import { ModuleTable } from "@/components/shared/ModuleTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { SectionCard } from "@/components/shared/SectionCard";
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

const TIPO_COLORS = {
  ANTICIPO: "#6366f1",
  PAGO_POR_FASE: "#3b82f6",
  PAGO_GENERAL: "#06b6d4",
};

const TIPO_LABELS = {
  ANTICIPO: "Anticipo",
  PAGO_POR_FASE: "Por fase",
  PAGO_GENERAL: "General",
};

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-sm border border-zinc-200 bg-white p-3 shadow-lg text-sm">
      <p className="font-semibold text-zinc-900 mb-2">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: entry.fill || entry.color }} />
          <span className="text-zinc-600">{TIPO_LABELS[entry.name] || entry.name}:</span>
          <span className="font-medium text-zinc-900">{formatCurrency(entry.value)}</span>
        </div>
      ))}
    </div>
  );
}

export default function FeedPage({ title, kicker, description, endpoint, columns }) {
  const [items, setItems] = useState(null);
  const [clients, setClients] = useState([]);
  const [draftFilters, setDraftFilters] = useState(baseFilters);
  const [filters, setFilters] = useState(baseFilters);

  const isPagos = endpoint === "/pagos";

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

  // Datos para el gráfico de barras agrupadas por proyecto
  const chartData = useMemo(() => {
    if (!isPagos || !items?.length) return [];
    const byProject = {};
    items.forEach((item) => {
      const key = item.codigoProyecto;
      if (!byProject[key]) {
        byProject[key] = {
          proyecto: key,
          nombreProyecto: item.projectName,
          ANTICIPO: 0,
          PAGO_POR_FASE: 0,
          PAGO_GENERAL: 0,
          total: 0,
        };
      }
      const tipo = item.payment?.tipoPago;
      const monto = Number(item.payment?.monto || 0);
      if (tipo && byProject[key][tipo] !== undefined) {
        byProject[key][tipo] += monto;
      }
      byProject[key].total += monto;
    });
    return Object.values(byProject).sort((a, b) => b.total - a.total);
  }, [items, isPagos]);

  // Totales por tipo para las tarjetas de resumen
  const totalesPorTipo = useMemo(() => {
    if (!isPagos || !items?.length) return {};
    return items.reduce((acc, item) => {
      const tipo = item.payment?.tipoPago;
      const monto = Number(item.payment?.monto || 0);
      if (tipo) acc[tipo] = (acc[tipo] || 0) + monto;
      return acc;
    }, {});
  }, [items, isPagos]);

  if (!items) {
    return (
      <div className="rounded-sm border border-zinc-200 bg-white p-8 text-sm text-zinc-600"
        data-testid={`feed-loading-${title.toLowerCase().replace(/\s+/g, "-")}`}>
        Cargando {title.toLowerCase()}...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader kicker={kicker} title={title} description={description} />

      <FilterBar
        filters={draftFilters}
        setFilters={setDraftFilters}
        clients={clients}
        onApply={() => setFilters({ ...draftFilters })}
        onReset={() => { setDraftFilters(baseFilters); setFilters(baseFilters); }}
      />

      {/* Gráfico solo para la vista de Pagos */}
      {isPagos && chartData.length > 0 ? (
        <SectionCard
          title="Distribución de pagos por proyecto"
          description="Desglose por tipo de pago (anticipo, por fase y general) agrupado por proyecto."
          accent="blue"
        >
          {/* Tarjetas de totales por tipo */}
          <div className="mb-6 grid gap-4 md:grid-cols-3">
            {["ANTICIPO", "PAGO_POR_FASE", "PAGO_GENERAL"].map((tipo) => (
              <div key={tipo} className="rounded-sm border border-zinc-200 p-4"
                style={{ borderLeftWidth: 4, borderLeftColor: TIPO_COLORS[tipo] }}>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">
                  {TIPO_LABELS[tipo]}
                </p>
                <p className="mt-2 text-2xl font-semibold" style={{ color: TIPO_COLORS[tipo] }}>
                  {formatCurrency(totalesPorTipo[tipo] || 0)}
                </p>
              </div>
            ))}
          </div>

          {/* Gráfico de barras agrupadas */}
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="proyecto"
                tick={{ fontSize: 12, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => `$${(v / 1_000_000).toFixed(0)}M`}
                tick={{ fontSize: 11, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => TIPO_LABELS[value] || value}
                wrapperStyle={{ fontSize: 12, paddingTop: 16 }}
              />
              <Bar dataKey="ANTICIPO" fill={TIPO_COLORS.ANTICIPO} radius={[3, 3, 0, 0]} />
              <Bar dataKey="PAGO_POR_FASE" fill={TIPO_COLORS.PAGO_POR_FASE} radius={[3, 3, 0, 0]} />
              <Bar dataKey="PAGO_GENERAL" fill={TIPO_COLORS.PAGO_GENERAL} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>
      ) : null}

      {items.length ? (
        <ModuleTable columns={columns} items={items} />
      ) : (
        <EmptyState
          title={`Sin ${title.toLowerCase()} todavía`}
          description="Los registros aparecerán aquí conforme avances en los proyectos."
        />
      )}
    </div>
  );
}