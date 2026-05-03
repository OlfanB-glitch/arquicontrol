import { useCallback, useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  HelpCircle,
  LayoutDashboard,
  ScrollText,
  Users,
  X,
} from "lucide-react";

const TOUR_COMPLETED_KEY = "arquicontrol-tour-completed";

const TOUR_STEPS = [
  {
    id: "welcome",
    title: "¡Bienvenido a ArquiControl!",
    description:
      "Este es tu panel de gestión arquitectónica. Te daremos un paseo rápido por las funcionalidades principales para que puedas empezar a trabajar de inmediato.",
    icon: CheckCircle2,
    position: "center",
    highlight: null,
    route: "/dashboard",
  },
  {
    id: "sidebar",
    title: "Barra de navegación",
    description:
      "Desde aquí accedes a todos los módulos del sistema: Dashboard, Clientes, Proyectos, Pagos, Contratistas, Proveedores, Materiales, Compras, Documentos y Bitácora de auditoría.",
    icon: LayoutDashboard,
    position: "right",
    highlight: "[data-testid='sidebar-navigation']",
    route: "/dashboard",
  },
  {
    id: "dashboard-metrics",
    title: "Métricas principales",
    description:
      "Estas tarjetas resumen el estado general de tu estudio: cantidad de clientes, proyectos activos, alertas pendientes y pagos recientes. Haz clic en cualquiera para ir directamente a ese módulo.",
    icon: LayoutDashboard,
    position: "bottom",
    highlight: "[data-testid='dashboard-metric-clientes']",
    route: "/dashboard",
  },
  {
    id: "dashboard-charts",
    title: "Estado del portafolio",
    description:
      "Aquí ves la distribución de tus proyectos por estado (pendiente, en ejecución, finalizado, etc.) con barras de colores. Las alertas activas aparecen al lado, resaltadas en rojo o ámbar según su nivel de urgencia.",
    icon: LayoutDashboard,
    position: "bottom",
    highlight: "[data-testid='dashboard-status-chart-card']",
    route: "/dashboard",
  },
  {
    id: "clientes",
    title: "Gestión de Clientes",
    description:
      "Registra las personas o empresas que contratan tus servicios. Cada cliente se identifica con un número de documento único. Puedes buscar, editar y consultar todos los clientes desde esta vista. Al crear un proyecto, lo asociarás a uno de estos clientes.",
    icon: Users,
    position: "center",
    highlight: null,
    route: "/clientes",
  },
  {
    id: "proyectos",
    title: "Gestión de Proyectos",
    description:
      "Este es el corazón del sistema. Cada proyecto contiene fases, seguimientos, pagos, contratistas, compras y documentos. Crea un nuevo proyecto asociándolo a un cliente, define sus fases y comienza a registrar la operación.",
    icon: BriefcaseBusiness,
    position: "center",
    highlight: null,
    route: "/proyectos",
  },
  {
    id: "proyecto-detalle",
    title: "Detalle del proyecto",
    description:
      "Al abrir un proyecto verás su resumen completo: métricas financieras (contrato, pagado, saldo, avance), estado de las fases, y seis pestañas para gestionar seguimientos, pagos, contratistas, compras, documentos y auditoría. Cada cambio queda registrado automáticamente en la bitácora.",
    icon: BriefcaseBusiness,
    position: "center",
    highlight: null,
    route: "/proyectos",
  },
  {
    id: "bitacora",
    title: "Bitácora de auditoría",
    description:
      "Toda operación del sistema (crear proyecto, registrar pago, dar de baja una fase, etc.) queda trazada aquí automáticamente. Puedes filtrar por fecha, tipo de evento, usuario o proyecto. Esto garantiza trazabilidad total de cada decisión tomada.",
    icon: ScrollText,
    position: "center",
    highlight: null,
    route: "/bitacora",
  },
  {
    id: "reportes",
    title: "Reportes y exportaciones",
    description:
      "Dentro de cada proyecto encontrarás opciones para descargar: un PDF de resumen para el cliente (con estado, avance y corte financiero), un CSV consolidado de pagos y compras, y un CSV de pagos a contratistas. Estos reportes están listos para imprimir o enviar.",
    icon: BriefcaseBusiness,
    position: "center",
    highlight: null,
    route: "/proyectos",
  },
  {
    id: "baja-logica",
    title: "Baja lógica con motivo",
    description:
      "ArquiControl nunca borra datos. Cuando necesites eliminar un registro (fase, pago, seguimiento, etc.), el sistema te pedirá un motivo obligatorio. El registro queda marcado como inactivo pero se conserva en el historial para auditoría.",
    icon: CheckCircle2,
    position: "center",
    highlight: null,
    route: "/proyectos",
  },
  {
    id: "finish",
    title: "¡Listo para empezar!",
    description:
      "Ya conoces las funcionalidades principales de ArquiControl. Puedes repetir este tour en cualquier momento haciendo clic en el botón de ayuda (?) en la parte inferior izquierda. ¡Éxito con tus proyectos!",
    icon: CheckCircle2,
    position: "center",
    highlight: null,
    route: null,
  },
];

export function GuidedTour() {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [tooltipStyle, setTooltipStyle] = useState({});
  const navigate = useNavigate();
  const location = useLocation();

  const step = TOUR_STEPS[currentStep];
  const isFirst = currentStep === 0;
  const isLast = currentStep === TOUR_STEPS.length - 1;
  const progress = ((currentStep + 1) / TOUR_STEPS.length) * 100;

  // Iniciar tour automáticamente la primera vez
  useEffect(() => {
    const completed = localStorage.getItem(TOUR_COMPLETED_KEY);
    if (!completed && location.pathname === "/dashboard") {
      const timer = setTimeout(() => setIsActive(true), 1200);
      return () => clearTimeout(timer);
    }
  }, [location.pathname]);

  // Posicionar tooltip cuando cambia el paso
  const positionTooltip = useCallback(() => {
    if (!step?.highlight) {
      setTooltipStyle({
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      });
      return;
    }

    const el = document.querySelector(step.highlight);
    if (!el) {
      setTooltipStyle({
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      });
      return;
    }

    const rect = el.getBoundingClientRect();
    const pos = step.position || "bottom";

    if (pos === "right") {
      setTooltipStyle({
        position: "fixed",
        top: `${Math.max(rect.top, 80)}px`,
        left: `${rect.right + 16}px`,
        transform: "none",
      });
    } else if (pos === "bottom") {
      setTooltipStyle({
        position: "fixed",
        top: `${rect.bottom + 16}px`,
        left: `${Math.max(rect.left, 280)}px`,
        transform: "none",
      });
    } else {
      setTooltipStyle({
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      });
    }
  }, [step]);

  useEffect(() => {
    if (!isActive) return;
    positionTooltip();
    window.addEventListener("resize", positionTooltip);
    return () => window.removeEventListener("resize", positionTooltip);
  }, [isActive, currentStep, positionTooltip]);

  function handleNext() {
    if (isLast) {
      finishTour();
      return;
    }
    const nextStep = TOUR_STEPS[currentStep + 1];
    if (nextStep.route && nextStep.route !== location.pathname) {
      navigate(nextStep.route);
    }
    setCurrentStep((s) => s + 1);
  }

  function handlePrev() {
    if (isFirst) return;
    const prevStep = TOUR_STEPS[currentStep - 1];
    if (prevStep.route && prevStep.route !== location.pathname) {
      navigate(prevStep.route);
    }
    setCurrentStep((s) => s - 1);
  }

  function finishTour() {
    localStorage.setItem(TOUR_COMPLETED_KEY, "true");
    setIsActive(false);
    setCurrentStep(0);
    navigate("/dashboard");
  }

  function skipTour() {
    localStorage.setItem(TOUR_COMPLETED_KEY, "true");
    setIsActive(false);
    setCurrentStep(0);
  }

  function restartTour() {
    setCurrentStep(0);
    navigate("/dashboard");
    setIsActive(true);
  }

  const StepIcon = step?.icon || CheckCircle2;

  if (!isActive) {
    return (
      <button
        type="button"
        onClick={restartTour}
        className="fixed bottom-6 left-6 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:shadow-xl hover:scale-110 lg:left-[272px]"
        title="Iniciar tour guiado"
        data-testid="tour-help-button"
      >
        <HelpCircle className="h-6 w-6" />
      </button>
    );
  }

  return (
    <>
      {/* Overlay oscuro */}
      <div
        className="fixed inset-0 z-[998] bg-black/50 transition-opacity duration-300"
        onClick={skipTour}
      />

      {/* Highlight sobre el elemento si existe */}
      {step.highlight && document.querySelector(step.highlight) ? (
        <HighlightBox selector={step.highlight} />
      ) : null}

      {/* Tooltip del paso actual */}
      <div
        className="fixed z-[1000] w-[420px] max-w-[90vw] animate-fade-in"
        style={tooltipStyle}
        data-testid={`tour-step-${step.id}`}
      >
        <div className="rounded-lg border border-zinc-200 bg-white shadow-2xl">
          {/* Header del tooltip */}
          <div className="flex items-center justify-between border-b border-zinc-100 px-5 py-3">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                {currentStep + 1}
              </span>
              <span className="text-xs text-zinc-500">
                de {TOUR_STEPS.length} pasos
              </span>
            </div>
            <button
              type="button"
              onClick={skipTour}
              className="rounded-sm p-1 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700"
              data-testid="tour-skip-button"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Barra de progreso */}
          <div className="h-1 w-full bg-zinc-100">
            <div
              className="h-full rounded-r-full bg-blue-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Contenido */}
          <div className="px-5 py-4">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50">
                <StepIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-zinc-900">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-600">
                  {step.description}
                </p>
              </div>
            </div>
          </div>

          {/* Acciones */}
          <div className="flex items-center justify-between border-t border-zinc-100 px-5 py-3">
            <button
              type="button"
              onClick={skipTour}
              className="text-xs text-zinc-400 hover:text-zinc-600"
              data-testid="tour-skip-text"
            >
              Saltar tour
            </button>
            <div className="flex gap-2">
              {!isFirst ? (
                <button
                  type="button"
                  onClick={handlePrev}
                  className="flex items-center gap-1 rounded-sm border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
                  data-testid="tour-prev-button"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Anterior
                </button>
              ) : null}
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-1 rounded-sm bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                data-testid="tour-next-button"
              >
                {isLast ? "Finalizar" : "Siguiente"}
                {!isLast ? <ArrowRight className="h-3.5 w-3.5" /> : null}
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
}

/* Componente auxiliar: recuadro brillante sobre el elemento resaltado */
function HighlightBox({ selector }) {
  const [rect, setRect] = useState(null);

  useEffect(() => {
    function update() {
      const el = document.querySelector(selector);
      if (el) setRect(el.getBoundingClientRect());
    }
    update();
    window.addEventListener("resize", update);
    window.addEventListener("scroll", update);
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", update);
    };
  }, [selector]);

  if (!rect) return null;

  return (
    <div
      className="fixed z-[999] rounded-sm border-2 border-blue-400 shadow-[0_0_0_9999px_rgba(0,0,0,0.45)]"
      style={{
        top: rect.top - 6,
        left: rect.left - 6,
        width: rect.width + 12,
        height: rect.height + 12,
        pointerEvents: "none",
      }}
    />
  );
}