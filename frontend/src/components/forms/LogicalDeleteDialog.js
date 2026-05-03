import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

export function LogicalDeleteDialog({ open, onOpenChange, target, onConfirm, isSubmitting }) {
  const [motivo, setMotivo] = useState("");

  useEffect(() => {
    if (!open) {
      setMotivo("");
    }
  }, [open]);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!motivo.trim()) {
      return;
    }
    await onConfirm(motivo.trim());
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-sm border-zinc-200 bg-white shadow-2xl">
        <DialogHeader>
          <DialogTitle data-testid="logical-delete-dialog-title">Confirmar baja lógica</DialogTitle>
          <DialogDescription data-testid="logical-delete-dialog-description">
            Esta acción desactivará el registro seleccionado y conservará su trazabilidad para auditoría. Debes indicar un motivo obligatorio para continuar.
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="rounded-sm border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-700" data-testid="logical-delete-dialog-target-box">
            <p><span className="font-semibold text-zinc-900">Elemento:</span> {target?.label || "—"}</p>
            <p className="mt-1"><span className="font-semibold text-zinc-900">Tipo:</span> {target?.type || "Subregistro"}</p>
          </div>

          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Motivo de la baja lógica (obligatorio)</span>
            <Textarea
              value={motivo}
              onChange={(event) => setMotivo(event.target.value)}
              className="min-h-[120px] rounded-sm border-zinc-300 shadow-none focus-visible:ring-zinc-900"
              placeholder="Explica brevemente por qué este registro debe quedar inactivo."
              data-testid="logical-delete-dialog-reason-input"
            />
          </label>

          <DialogFooter>
            <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => onOpenChange(false)} data-testid="logical-delete-dialog-cancel-button">
              Cancelar
            </Button>
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" disabled={isSubmitting || !motivo.trim()} data-testid="logical-delete-dialog-confirm-button">
              {isSubmitting ? "Procesando..." : "Confirmar baja lógica"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}