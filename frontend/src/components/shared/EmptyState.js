export function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-sm border border-dashed border-zinc-300 bg-white px-6 py-12 text-center" data-testid={`empty-state-${title.toLowerCase().replace(/\s+/g, "-")}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-zinc-500">Sin registros</p>
      <h3 className="mt-3 text-xl font-semibold text-zinc-950">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm text-zinc-600">{description}</p>
      {action ? <div className="mt-6 flex justify-center">{action}</div> : null}
    </div>
  );
}