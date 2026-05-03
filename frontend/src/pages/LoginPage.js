import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Building2, Eye, EyeOff, Lock, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { LOGIN_BACKGROUND_URL } from "@/lib/catalogs";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formState, setFormState] = useState({ email: "", password: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!formState.email || !formState.password) {
      setError("Ingresa correo y contraseña para continuar.");
      return;
    }
    setIsSubmitting(true);
    setError("");
    try {
      await login(formState);
      navigate("/dashboard");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Credenciales incorrectas. Verifica e intenta de nuevo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid min-h-screen bg-zinc-50 lg:grid-cols-[1fr_1.15fr]">
      <section className="relative flex items-center justify-center px-6 py-12 md:px-12">
        <div className="w-full max-w-md" data-testid="login-panel">
          {/* Logo / Branding */}
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-zinc-900">
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-lg font-bold tracking-tight text-zinc-950" data-testid="login-brand">ArquiControl</p>
              <p className="text-xs text-zinc-500">Sistema de gestión arquitectónica</p>
            </div>
          </div>

          {/* Título */}
          <h1 className="mt-8 text-3xl font-bold tracking-tight text-zinc-950" data-testid="login-title">
            Iniciar sesión
          </h1>
          <p className="mt-2 text-sm text-zinc-600" data-testid="login-description">
            Ingresa tus credenciales para acceder al panel de gestión.
          </p>

          {/* Formulario */}
          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Correo electrónico</span>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <Input
                  type="email"
                  placeholder="tu@correo.com"
                  value={formState.email}
                  onChange={(e) => { setFormState((c) => ({ ...c, email: e.target.value })); setError(""); }}
                  className="rounded-sm border-zinc-300 pl-10 shadow-none focus-visible:ring-blue-500"
                  data-testid="login-email-input"
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Contraseña</span>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={formState.password}
                  onChange={(e) => { setFormState((c) => ({ ...c, password: e.target.value })); setError(""); }}
                  className="rounded-sm border-zinc-300 pl-10 pr-10 shadow-none focus-visible:ring-blue-500"
                  data-testid="login-password-input"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-700"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  data-testid="login-toggle-password"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </label>

            {/* Error */}
            {error ? (
              <div className="flex items-start gap-2 rounded-sm border border-red-200 bg-red-50 px-4 py-3" data-testid="login-error-message">
                <span className="mt-0.5 text-sm text-red-500">⚠</span>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            ) : null}

            {/* Botón submit */}
            <Button
              type="submit"
              className="w-full rounded-sm bg-zinc-900 py-6 text-white hover:bg-zinc-800 disabled:opacity-60"
              disabled={isSubmitting}
              data-testid="login-submit-button"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Verificando...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Ingresar
                  <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>
          </form>

          {/* Footer */}
          <p className="mt-8 text-center text-xs text-zinc-400">
            © 2026 ArquiControl · Proyecto académico
          </p>
        </div>
      </section>

      {/* Panel visual derecho */}
      <section
        className="relative hidden overflow-hidden lg:block"
        style={{ backgroundImage: `url(${LOGIN_BACKGROUND_URL})`, backgroundSize: "cover", backgroundPosition: "center" }}
      >
        <div className="absolute inset-0 bg-zinc-950/60" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />
        <div className="relative flex h-full flex-col items-start justify-end p-12">
          <div className="max-w-lg space-y-6">
            <div className="flex gap-3">
              <div className="h-1 w-8 rounded-full bg-blue-400" />
              <div className="h-1 w-8 rounded-full bg-emerald-400" />
              <div className="h-1 w-8 rounded-full bg-amber-400" />
            </div>
            <h2 className="text-3xl font-semibold tracking-tight text-white">
              Gestión integral de proyectos arquitectónicos
            </h2>
            <div className="flex flex-wrap gap-2">
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Clientes</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Proyectos</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Pagos</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Contratistas</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Documentos</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Auditoría</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}