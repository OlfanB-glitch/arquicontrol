export function PageHeader({ kicker, title, description, actions }) {
  return (
    <div className="mb-8 flex flex-col gap-4 border-b border-zinc-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div className="max-w-3xl">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-500" data-testid={`page-header-kicker-${title.toLowerCase().replace(/\s+/g, "-")}`}>
          {kicker}
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-zinc-950" data-testid={`page-header-title-${title.toLowerCase().replace(/\s+/g, "-")}`}>
          {title}
        </h1>
        <p className="mt-3 max-w-2xl text-base text-zinc-700" data-testid={`page-header-description-${title.toLowerCase().replace(/\s+/g, "-")}`}>
          {description}
        </p>
      </div>
      {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
    </div>
  );
}