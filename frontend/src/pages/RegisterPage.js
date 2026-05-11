import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Building2, Eye, EyeOff, Lock, Mail, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { LOGIN_BACKGROUND_URL } from "@/lib/catalogs";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formState, setFormState] = useState({ nombreCompleto: "", email: "", password: "", confirmPassword: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!formState.nombreCompleto || !formState.email || !formState.password || !formState.confirmPassword) {
      setError("Todos los campos son obligatorios.");
      return;
    }
    if (formState.password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (formState.password !== formState.confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setIsSubmitting(true);
    setError("");
    try {
      const { default: api } = await import("@/lib/api");
      const response = await api.post("/auth/register", formState);
      // Auto-login después del registro
      const { setAuthToken } = await import("@/lib/api");
      localStorage.setItem("arquicontrol-session-token", response.data.token);
      setAuthToken(response.data.token);
      // Recargar para que AuthProvider detecte el nuevo token
      window.location.href = "/dashboard";
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "No fue posible crear la cuenta. Intenta de nuevo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid min-h-screen bg-zinc-50 lg:grid-cols-[1fr_1.15fr]">
      <section className="relative flex items-center justify-center px-6 py-12 md:px-12">
        <div className="w-full max-w-md" data-testid="register-panel">
          {/* Logo / Branding */}
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-zinc-900">
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-lg font-bold tracking-tight text-zinc-950" data-testid="register-brand">ArquiControl</p>
              <p className="text-xs text-zinc-500">Sistema de gestión arquitectónica</p>
            </div>
          </div>

          {/* Título */}
          <h1 className="mt-8 text-3xl font-bold tracking-tight text-zinc-950" data-testid="register-title">
            Crear cuenta
          </h1>
          <p className="mt-2 text-sm text-zinc-600" data-testid="register-description">
            Regístrate para acceder al panel de gestión de proyectos.
          </p>

          {/* Formulario */}
          <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Nombre completo</span>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <Input
                  type="text"
                  placeholder="Tu nombre completo"
                  value={formState.nombreCompleto}
                  onChange={(e) => { setFormState((c) => ({ ...c, nombreCompleto: e.target.value })); setError(""); }}
                  className="rounded-sm border-zinc-300 pl-10 shadow-none focus-visible:ring-blue-500"
                  data-testid="register-name-input"
                />
              </div>
            </label>

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
                  data-testid="register-email-input"
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Contraseña</span>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Mínimo 8 caracteres"
                  value={formState.password}
                  onChange={(e) => { setFormState((c) => ({ ...c, password: e.target.value })); setError(""); }}
                  className="rounded-sm border-zinc-300 pl-10 pr-10 shadow-none focus-visible:ring-blue-500"
                  data-testid="register-password-input"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-700"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  data-testid="register-toggle-password"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">Confirmar contraseña</span>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Repite la contraseña"
                  value={formState.confirmPassword}
                  onChange={(e) => { setFormState((c) => ({ ...c, confirmPassword: e.target.value })); setError(""); }}
                  className="rounded-sm border-zinc-300 pl-10 shadow-none focus-visible:ring-blue-500"
                  data-testid="register-confirm-password-input"
                />
              </div>
            </label>

            {/* Error */}
            {error ? (
              <div className="flex items-start gap-2 rounded-sm border border-red-200 bg-red-50 px-4 py-3" data-testid="register-error-message">
                <span className="mt-0.5 text-sm text-red-500">⚠</span>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            ) : null}

            {/* Botón submit */}
            <Button
              type="submit"
              className="w-full rounded-sm bg-zinc-900 py-6 text-white hover:bg-zinc-800 disabled:opacity-60"
              disabled={isSubmitting}
              data-testid="register-submit-button"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Creando cuenta...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Crear cuenta
                  <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>
          </form>

          {/* Link a login */}
          <p className="mt-6 text-center text-sm text-zinc-600">
            ¿Ya tienes cuenta?{" "}
            <Link to="/login" className="font-semibold text-zinc-900 underline-offset-4 hover:underline" data-testid="register-login-link">
              Inicia sesión
            </Link>
          </p>

          {/* Footer */}
          <p className="mt-6 text-center text-xs text-zinc-400">
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
              Centraliza la gestión de tus proyectos arquitectónicos
            </h2>
            <div className="flex flex-wrap gap-2">
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Clientes</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Proyectos</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Pagos</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Contratistas</span>
              <span className="rounded-sm border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90">Auditoría</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}