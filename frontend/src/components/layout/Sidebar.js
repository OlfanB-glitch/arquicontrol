import { NavLink } from "react-router-dom";
import {
  Banknote,
  BriefcaseBusiness,
  Building2,
  FileText,
  LayoutDashboard,
  LogOut,
  Package,
  ScrollText,
  Truck,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { getInitials } from "@/lib/utils";

const navigation = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, testId: "sidebar-link-dashboard" },
  { to: "/clientes", label: "Clientes", icon: Users, testId: "sidebar-link-clientes" },
  { to: "/proyectos", label: "Proyectos", icon: BriefcaseBusiness, testId: "sidebar-link-proyectos" },
  { to: "/bitacora", label: "Bitácora", icon: ScrollText, testId: "sidebar-link-bitacora" },
  { to: "/pagos", label: "Pagos", icon: Banknote, testId: "sidebar-link-pagos" },
  { to: "/contratistas", label: "Contratistas", icon: Building2, testId: "sidebar-link-contratistas" },
  { to: "/proveedores", label: "Proveedores", icon: Truck, testId: "sidebar-link-proveedores" },
  { to: "/materiales", label: "Materiales", icon: Package, testId: "sidebar-link-materiales" },
  { to: "/compras", label: "Compras", icon: FileText, testId: "sidebar-link-compras" },
  { to: "/documentos", label: "Documentos", icon: FileText, testId: "sidebar-link-documentos" },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-zinc-800 bg-zinc-950 lg:flex lg:flex-col">
      <div className="border-b border-zinc-800 px-6 py-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500" data-testid="sidebar-brand-kicker">
          ArquiControl
        </p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-white" data-testid="sidebar-brand-title">
          Panel técnico
        </h1>
        <p className="mt-2 text-sm text-zinc-400" data-testid="sidebar-brand-description">
          Controla clientes, obra, pagos y evidencia en un solo lugar.
        </p>
      </div>

      <nav className="flex-1 space-y-1 px-4 py-6" data-testid="sidebar-navigation">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              data-testid={item.testId}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 border-l-2 px-4 py-3 text-sm transition-colors duration-200",
                  isActive
                    ? "border-white bg-zinc-900 text-white"
                    : "border-transparent text-zinc-400 hover:bg-zinc-900/70 hover:text-zinc-100",
                ].join(" ")
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-zinc-800 px-4 py-5">
        <div className="mb-4 flex items-center gap-3 rounded-sm border border-zinc-800 bg-zinc-900/70 px-3 py-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-sm border border-zinc-700 bg-zinc-950 text-sm font-semibold text-zinc-100" data-testid="sidebar-user-avatar">
            {getInitials(user?.nombreCompleto)}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-zinc-100" data-testid="sidebar-user-name">
              {user?.nombreCompleto}
            </p>
            <p className="truncate text-xs uppercase tracking-[0.12em] text-zinc-500" data-testid="sidebar-user-role">
              {user?.rol}
            </p>
          </div>
        </div>

        <Button
          variant="outline"
          className="w-full rounded-sm border-zinc-700 bg-zinc-950 text-zinc-100 hover:bg-zinc-900 hover:text-white"
          onClick={logout}
          data-testid="sidebar-logout-button"
        >
          <LogOut className="h-4 w-4" />
          Cerrar sesión
        </Button>
      </div>
    </aside>
  );
}