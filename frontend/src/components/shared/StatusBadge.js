import { statusStyles } from "@/lib/catalogs";

const statusIcons = {
  PENDIENTE: "○",
  EN_COTIZACION: "◎",
  EN_DISENO: "◈",
  EN_EJECUCION: "▶",
  SUSPENDIDO: "⏸",
  FINALIZADO: "✓",
  ENTREGADO: "★",
  ACTIVO: "●",
  INACTIVO: "○",
  ACTIVA: "●",
  SUSPENDIDA: "⏸",
  FINALIZADA: "✓",
  INACTIVA: "○",
  ANTICIPO: "◇",
  PAGO_POR_FASE: "◆",
  PAGO_GENERAL: "■",
  ALERTA_PAGO: "⚠",
  PROYECTO_ATRASADO: "⏰",
};

export function StatusBadge({ value, testId }) {
  const icon = statusIcons[value] || "";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-sm border px-2.5 py-1 text-xs font-semibold tracking-[0.08em] ${statusStyles[value] || "border-zinc-300 bg-zinc-100 text-zinc-700"}`}
      data-testid={testId}
    >
      {icon ? <span className="text-[10px]">{icon}</span> : null}
      {value || "SIN_ESTADO"}
    </span>
  );
}