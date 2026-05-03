import { useState } from "react";
import { useLocation } from "react-router-dom";
import { LogOut, Menu, User, X } from "lucide-react";

import { GuidedTour } from "@/components/layout/GuidedTour";
import { Sidebar } from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { getInitials } from "@/lib/utils";

const pageTitles = {
  "/dashboard": "Dashboard",
  "/clientes": "Clientes",
  "/proyectos": "Proyectos",
  "/bitacora": "Bitácora",
  "/pagos": "Pagos",
  "/contratistas": "Contratistas",
  "/proveedores": "Proveedores",
  "/materiales": "Materiales",
  "/compras": "Compras",
  "/documentos": "Documentos",
};

export function AppShell({ children }) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);

  const title = location.pathname.startsWith("/proyectos/")
    ? "Detalle del proyecto"
    : pageTitles[location.pathname] || "ArquiControl";

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-950">
      <Sidebar />

      {/* Overlay del sidebar en móvil */}
      {showMobileSidebar ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowMobileSidebar(false)} />
          <div className="relative z-50 h-full w-64">
            <Sidebar />
          </div>
        </div>
      ) : null}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-zinc-200 bg-zinc-50/90 backdrop-blur-sm">
          <div className="architect-container flex items-center justify-between gap-4 py-4">
            <div className="flex items-center gap-4">
              {/* Botón hamburguesa en móvil */}
              <Button
                type="button"
                variant="ghost"
                className="rounded-sm text-zinc-700 hover:bg-zinc-200 lg:hidden"
                onClick={() => setShowMobileSidebar(true)}
                data-testid="app-header-mobile-menu-button"
              >
                <Menu className="h-5 w-5" />
              </Button>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500" data-testid="app-header-kicker">
                  Gestión integral del estudio
                </p>
                <h2 className="mt-1 text-xl font-semibold tracking-tight text-zinc-950 lg:text-2xl" data-testid="app-header-title">
                  {title}
                </h2>
              </div>
            </div>

            {/* Menú de usuario */}
            <div className="relative">
              <button
                type="button"
                className="flex items-center gap-3 rounded-sm border border-zinc-200 bg-white px-3 py-2 text-left transition-colors hover:bg-zinc-50"
                onClick={() => setShowUserMenu(!showUserMenu)}
                data-testid="app-header-user-button"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-semibold text-white" data-testid="app-header-user-avatar">
                  {getInitials(user?.nombreCompleto)}
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-zinc-900" data-testid="app-header-user-name">{user?.nombreCompleto}</p>
                  <p className="text-xs text-zinc-500" data-testid="app-header-user-email">{user?.email}</p>
                </div>
              </button>

              {/* Dropdown del usuario */}
              {showUserMenu ? (
                <>
                  <div className="fixed inset-0 z-30" onClick={() => setShowUserMenu(false)} />
                  <div className="absolute right-0 top-full z-40 mt-2 w-72 rounded-sm border border-zinc-200 bg-white shadow-lg" data-testid="app-header-user-dropdown">
                    <div className="border-b border-zinc-200 px-4 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
                          {getInitials(user?.nombreCompleto)}
                        </div>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-zinc-900">{user?.nombreCompleto}</p>
                          <p className="truncate text-xs text-zinc-500">{user?.email}</p>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center gap-2">
                        <span className="inline-flex items-center gap-1 rounded-sm border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700">
                          <User className="h-3 w-3" /> {user?.rol}
                        </span>
                      </div>
                    </div>

                    <div className="p-2">
                      <button
                        type="button"
                        className="flex w-full items-center gap-3 rounded-sm px-3 py-2.5 text-sm text-red-600 transition-colors hover:bg-red-50"
                        onClick={() => {
                          setShowUserMenu(false);
                          logout();
                        }}
                        data-testid="app-header-logout-button"
                      >
                        <LogOut className="h-4 w-4" />
                        Cerrar sesión
                      </button>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          </div>
        </header>

        <main className="architect-container py-8" data-testid="app-main-content">
          {children}
        </main>
      </div>

      {/* Tour guiado interactivo */}
      <GuidedTour />
    </div>
  );
}