import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const colorVariants = {
  blue: "border-l-4 border-l-blue-500",
  green: "border-l-4 border-l-emerald-500",
  amber: "border-l-4 border-l-amber-500",
  red: "border-l-4 border-l-red-500",
  purple: "border-l-4 border-l-violet-500",
  teal: "border-l-4 border-l-teal-500",
  default: "border-l-4 border-l-zinc-300",
};

const iconColors = {
  blue: "text-blue-600",
  green: "text-emerald-600",
  amber: "text-amber-600",
  red: "text-red-600",
  purple: "text-violet-600",
  teal: "text-teal-600",
  default: "text-zinc-400",
};

const valueColors = {
  blue: "text-blue-700",
  green: "text-emerald-700",
  amber: "text-amber-700",
  red: "text-red-700",
  purple: "text-violet-700",
  teal: "text-teal-700",
  default: "text-zinc-950",
};

export function MetricCard({ title, value, detail, icon: Icon, color = "default", href, testId }) {
  const navigate = useNavigate();
  const borderClass = colorVariants[color] || colorVariants.default;
  const iconClass = iconColors[color] || iconColors.default;
  const valueClass = valueColors[color] || valueColors.default;
  const isClickable = Boolean(href);

  function handleClick() {
    if (href) navigate(href);
  }

  return (
    <Card
      className={`rounded-sm border-zinc-200 bg-white shadow-none ${borderClass} ${isClickable ? "cursor-pointer transition-all duration-200 hover:shadow-md hover:border-zinc-300 hover:-translate-y-0.5" : ""}`}
      onClick={handleClick}
      data-testid={testId}
    >
      <CardHeader className="border-b border-zinc-200 pb-4">
        <div className="flex items-center justify-between gap-3">
          <CardTitle className="text-sm font-semibold uppercase tracking-[0.12em] text-zinc-500">{title}</CardTitle>
          <div className="flex items-center gap-2">
            {isClickable ? <span className="text-xs text-zinc-400">Ver →</span> : null}
            {Icon ? <Icon className={`h-5 w-5 ${iconClass}`} /> : null}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-5">
        <p className={`text-3xl font-semibold tracking-tight ${valueClass}`} data-testid={`${testId}-value`}>
          {value}
        </p>
        <p className="mt-2 text-sm text-zinc-600" data-testid={`${testId}-detail`}>
          {detail}
        </p>
      </CardContent>
    </Card>
  );
}