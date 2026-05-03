const accentVariants = {
  blue: "border-t-2 border-t-blue-500",
  green: "border-t-2 border-t-emerald-500",
  amber: "border-t-2 border-t-amber-500",
  red: "border-t-2 border-t-red-500",
  purple: "border-t-2 border-t-violet-500",
  teal: "border-t-2 border-t-teal-500",
};

export function SectionCard({ title, description, actions, children, testId, accent }) {
  const accentClass = accent ? accentVariants[accent] || "" : "";

  return (
    <section className={`rounded-sm border border-zinc-200 bg-white ${accentClass}`} data-testid={testId}>
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-zinc-200 px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Sección</p>
          <h3 className="mt-2 text-lg font-semibold text-zinc-950">{title}</h3>
          {description ? <p className="mt-2 text-sm text-zinc-600">{description}</p> : null}
        </div>
        {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}