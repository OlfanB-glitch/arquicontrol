import { ThemeProvider } from "next-themes";
import "@/App.css";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/hooks/useAuth";
import { entityModules } from "@/lib/catalogs";
import { openDocumentResource } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import DashboardPage from "@/pages/DashboardPage";
import EntityPage from "@/pages/EntityPage";
import FeedPage from "@/pages/FeedPage";
import AuditLogPage from "@/pages/AuditLogPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProjectDetailPage from "@/pages/ProjectDetailPage";
import ProjectsPage from "@/pages/ProjectsPage";

function ProtectedLayout() {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return <div className="flex min-h-screen items-center justify-center bg-zinc-50 text-sm text-zinc-600" data-testid="app-auth-loading">Cargando sesión...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

function App() {
  return (
    <div className="App">
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
              <Route path="/" element={<ProtectedLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="bitacora" element={<AuditLogPage />} />
                <Route path="clientes" element={<EntityPage moduleKey="clientes" config={entityModules.clientes} />} />
                <Route path="contratistas" element={<EntityPage moduleKey="contratistas" config={entityModules.contratistas} />} />
                <Route path="proveedores" element={<EntityPage moduleKey="proveedores" config={entityModules.proveedores} />} />
                <Route path="materiales" element={<EntityPage moduleKey="materiales" config={entityModules.materiales} />} />
                <Route path="proyectos" element={<ProjectsPage />} />
                <Route path="proyectos/:projectId" element={<ProjectDetailPage />} />
                <Route
                  path="pagos"
                  element={(
                    <FeedPage
                      kicker="Flujo financiero"
                      title="Pagos"
                      description="Vista transversal de pagos recibidos por proyecto, útil para conciliación y control de saldo pendiente."
                      endpoint="/pagos"
                      columns={[
                        { key: "codigoProyecto", label: "Código" },
                        { key: "projectName", label: "Proyecto" },
                        { key: "payment.tipoPago", label: "Tipo", render: (item) => <StatusBadge value={item.payment?.tipoPago} testId={`payments-feed-badge-${item.payment?.idPago}`} /> },
                        { key: "payment.fechaPago", label: "Fecha", render: (item) => formatDate(item.payment?.fechaPago) },
                        { key: "payment.monto", label: "Monto", render: (item) => formatCurrency(item.payment?.monto) },
                      ]}
                    />
                  )}
                />
                <Route
                  path="compras"
                  element={(
                    <FeedPage
                      kicker="Control de adquisiciones"
                      title="Compras"
                      description="Consulta compras recientes, su factura y el monto total consumido por proyecto."
                      endpoint="/compras"
                      columns={[
                        { key: "codigoProyecto", label: "Código" },
                        { key: "projectName", label: "Proyecto" },
                        { key: "purchase.numeroFactura", label: "Factura" },
                        { key: "purchase.fechaCompra", label: "Fecha", render: (item) => formatDate(item.purchase?.fechaCompra) },
                        { key: "purchase.total", label: "Total", render: (item) => formatCurrency(item.purchase?.total) },
                      ]}
                    />
                  )}
                />
                <Route
                  path="documentos"
                  element={(
                    <FeedPage
                      kicker="Trazabilidad documental"
                      title="Documentos"
                      description="Reúne contratos, especificaciones, evidencias y archivos vinculados a los proyectos del estudio."
                      endpoint="/documentos"
                      columns={[
                        { key: "codigoProyecto", label: "Código" },
                        { key: "projectName", label: "Proyecto" },
                        { key: "document.tipo", label: "Tipo", render: (item) => <StatusBadge value={item.document?.tipo} testId={`documents-feed-badge-${item.document?.id}`} /> },
                        { key: "document.nombre", label: "Nombre" },
                        { key: "document.fechaRegistro", label: "Fecha", render: (item) => formatDate(item.document?.fechaRegistro) },
                        { key: "document.url", label: "Enlace", render: (item) => <button type="button" className="text-zinc-900 underline-offset-4 hover:underline" onClick={() => openDocumentResource(item.document?.url)} data-testid={`documents-feed-link-${item.document?.id}`}>Abrir</button> },
                      ]}
                    />
                  )}
                />
              </Route>
            </Routes>
          </BrowserRouter>
          <Toaster position="top-right" />
        </AuthProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;