import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function FilterBar({ filters, setFilters, clients = [], onApply, onReset, amountLabel = "Monto" }) {
  return (
    <form
      className="grid gap-3 rounded-sm border border-zinc-200 bg-white p-4 lg:grid-cols-4 xl:grid-cols-8"
      onSubmit={(event) => {
        event.preventDefault();
        onApply();
      }}
      data-testid="advanced-filter-bar"
    >
      <Input
        placeholder="Búsqueda global"
        value={filters.q}
        onChange={(event) => setFilters((current) => ({ ...current, q: event.target.value }))}
        data-testid="filter-input-q"
      />

      <select
        className="flex h-9 w-full rounded-md border border-zinc-300 bg-white px-3 text-sm"
        value={filters.estado}
        onChange={(event) => setFilters((current) => ({ ...current, estado: event.target.value }))}
        data-testid="filter-input-estado"
      >
        <option value="">Todos los estados</option>
        {["PENDIENTE", "EN_COTIZACION", "EN_DISENO", "EN_EJECUCION", "SUSPENDIDO", "FINALIZADO", "ENTREGADO"].map((status) => (
          <option key={status} value={status}>{status}</option>
        ))}
      </select>

      <select
        className="flex h-9 w-full rounded-md border border-zinc-300 bg-white px-3 text-sm"
        value={filters.clienteId}
        onChange={(event) => setFilters((current) => ({ ...current, clienteId: event.target.value }))}
        data-testid="filter-input-cliente"
      >
        <option value="">Todos los clientes</option>
        {clients.map((client) => (
          <option key={client.id} value={client.id}>{client.nombreCompleto}</option>
        ))}
      </select>

      <Input
        type="date"
        value={filters.fechaDesde}
        onChange={(event) => setFilters((current) => ({ ...current, fechaDesde: event.target.value }))}
        data-testid="filter-input-fecha-desde"
      />

      <Input
        type="date"
        value={filters.fechaHasta}
        onChange={(event) => setFilters((current) => ({ ...current, fechaHasta: event.target.value }))}
        data-testid="filter-input-fecha-hasta"
      />

      <Input
        type="number"
        placeholder={`${amountLabel} mínimo`}
        value={filters.montoMin}
        onChange={(event) => setFilters((current) => ({ ...current, montoMin: event.target.value }))}
        data-testid="filter-input-monto-min"
      />

      <Input
        type="number"
        placeholder={`${amountLabel} máximo`}
        value={filters.montoMax}
        onChange={(event) => setFilters((current) => ({ ...current, montoMax: event.target.value }))}
        data-testid="filter-input-monto-max"
      />

      <div className="flex gap-2">
        <Button type="submit" className="flex-1 rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" data-testid="filter-apply-button">
          Aplicar
        </Button>
        <Button type="button" variant="outline" className="flex-1 rounded-sm border-zinc-300" onClick={onReset} data-testid="filter-reset-button">
          Limpiar
        </Button>
      </div>
    </form>
  );
}