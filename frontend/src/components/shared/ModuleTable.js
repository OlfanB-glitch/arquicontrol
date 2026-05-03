import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { resolveValue } from "@/lib/utils";

export function ModuleTable({ columns, items, onEdit, emptyMessage = "Sin registros todavía." }) {
  return (
    <div className="overflow-hidden rounded-sm border border-zinc-200 bg-white" data-testid="module-table-wrapper">
      <Table className="min-w-full">
        <TableHeader className="bg-zinc-50">
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column.key} className="h-11 px-4 text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">
                {column.label}
              </TableHead>
            ))}
            {onEdit ? <TableHead className="px-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Acciones</TableHead> : null}
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.length ? (
            items.map((item, index) => {
              const rowId = item.id || item.payment?.idPago || item.purchase?.idCompra || item.document?.id || `row-${index}`;
              return (
              <TableRow key={rowId} className="hover:bg-zinc-50" data-testid={`module-table-row-${rowId}`}>
                {columns.map((column) => (
                  <TableCell key={column.key} className="px-4 py-3 align-top text-sm text-zinc-700" data-testid={`module-table-cell-${rowId}-${column.key}`}>
                    {column.render ? column.render(item) : resolveValue(item, column.key) || "—"}
                  </TableCell>
                ))}
                {onEdit ? (
                  <TableCell className="px-4 py-3 text-right">
                    <Button
                      variant="ghost"
                      className="rounded-sm text-zinc-700 hover:bg-zinc-100"
                      onClick={() => onEdit(item)}
                      data-testid={`module-table-edit-button-${rowId}`}
                    >
                      Editar
                    </Button>
                  </TableCell>
                ) : null}
              </TableRow>
            )})
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length + (onEdit ? 1 : 0)} className="px-4 py-12 text-center text-sm text-zinc-500" data-testid="module-table-empty-state">
                {emptyMessage}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}