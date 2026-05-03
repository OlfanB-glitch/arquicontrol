export const LOGIN_BACKGROUND_URL =
  "https://images.pexels.com/photos/1872165/pexels-photo-1872165.jpeg";

export const PROJECT_TYPES = [
  "VIVIENDA",
  "REMODELACION",
  "AMPLIACION",
  "ADECUACION_INTERIOR",
  "DISENO_COMERCIAL",
  "OTRO",
];

export const PROJECT_STATUSES = [
  "PENDIENTE",
  "EN_COTIZACION",
  "EN_DISENO",
  "EN_EJECUCION",
  "SUSPENDIDO",
  "FINALIZADO",
  "ENTREGADO",
];

export const PAYMENT_TYPES = ["ANTICIPO", "PAGO_POR_FASE", "PAGO_GENERAL"];
export const ASSIGNMENT_STATUSES = ["ACTIVA", "SUSPENDIDA", "FINALIZADA"];
export const RECORD_STATUSES = ["ACTIVO", "INACTIVO"];

export const statusStyles = {
  // Estados de proyecto
  PENDIENTE: "border-zinc-300 bg-zinc-100 text-zinc-800",
  EN_COTIZACION: "border-sky-200 bg-sky-50 text-sky-700",
  EN_DISENO: "border-indigo-200 bg-indigo-50 text-indigo-700",
  EN_EJECUCION: "border-blue-200 bg-blue-50 text-blue-700",
  SUSPENDIDO: "border-amber-200 bg-amber-50 text-amber-700",
  FINALIZADO: "border-emerald-200 bg-emerald-50 text-emerald-700",
  ENTREGADO: "border-teal-200 bg-teal-50 text-teal-700",
  // Estados de registro
  ACTIVO: "border-emerald-200 bg-emerald-50 text-emerald-700",
  INACTIVO: "border-zinc-300 bg-zinc-100 text-zinc-700",
  ACTIVA: "border-emerald-200 bg-emerald-50 text-emerald-700",
  SUSPENDIDA: "border-amber-200 bg-amber-50 text-amber-700",
  FINALIZADA: "border-zinc-300 bg-zinc-100 text-zinc-700",
  INACTIVA: "border-zinc-300 bg-zinc-100 text-zinc-700",
  // Tipos de pago
  ANTICIPO: "border-violet-200 bg-violet-50 text-violet-700",
  PAGO_POR_FASE: "border-blue-200 bg-blue-50 text-blue-700",
  PAGO_GENERAL: "border-cyan-200 bg-cyan-50 text-cyan-700",
  // Alertas
  ALERTA_PAGO: "border-red-200 bg-red-50 text-red-700",
  PROYECTO_ATRASADO: "border-orange-200 bg-orange-50 text-orange-700",
  // Tipos de documento
  DOCUMENTO: "border-slate-200 bg-slate-50 text-slate-700",
  EVIDENCIA: "border-lime-200 bg-lime-50 text-lime-700",
  CONTRATO: "border-amber-200 bg-amber-50 text-amber-700",
  PLANO: "border-blue-200 bg-blue-50 text-blue-700",
  ARCHIVO: "border-purple-200 bg-purple-50 text-purple-700",
};

// Colores para las barras de estado del dashboard
export const statusBarColors = {
  PENDIENTE: "bg-zinc-400",
  EN_COTIZACION: "bg-sky-500",
  EN_DISENO: "bg-indigo-500",
  EN_EJECUCION: "bg-blue-600",
  SUSPENDIDO: "bg-amber-500",
  FINALIZADO: "bg-emerald-500",
  ENTREGADO: "bg-teal-500",
};

export const entityModules = {
  clientes: {
    title: "Clientes",
    description: "Centraliza contactos, facturación y relación con proyectos activos.",
    endpoint: "/clientes",
    singular: "cliente",
    fields: [
      { name: "tipoDocumento", label: "Tipo documento", type: "text", required: true },
      { name: "numeroDocumento", label: "Número documento", type: "text", required: true },
      { name: "nombreCompleto", label: "Nombre completo", type: "text", required: true },
      { name: "telefono", label: "Teléfono", type: "tel", required: true },
      { name: "correo", label: "Correo", type: "email", required: true },
      { name: "direccion", label: "Dirección", type: "text", required: true },
      { name: "ciudad", label: "Ciudad", type: "text", required: true },
      { name: "fechaPrimerContacto", label: "Primer contacto", type: "date", required: true },
      { name: "estado", label: "Estado", type: "select", required: true, options: RECORD_STATUSES },
      { name: "observaciones", label: "Observaciones", type: "textarea" },
    ],
  },
  contratistas: {
    title: "Contratistas",
    description: "Gestiona especialistas externos, su tarifa y disponibilidad para proyectos.",
    endpoint: "/contratistas",
    singular: "contratista",
    fields: [
      { name: "tipoDocumento", label: "Tipo documento", type: "text", required: true },
      { name: "numeroDocumento", label: "Número documento", type: "text", required: true },
      { name: "nombreCompleto", label: "Nombre completo", type: "text", required: true },
      { name: "especialidad", label: "Especialidad", type: "text", required: true },
      { name: "telefono", label: "Teléfono", type: "tel", required: true },
      { name: "correo", label: "Correo", type: "email", required: true },
      { name: "direccion", label: "Dirección", type: "text", required: true },
      { name: "tarifaBase", label: "Tarifa base", type: "number", required: true, min: 0 },
      { name: "estado", label: "Estado", type: "select", required: true, options: RECORD_STATUSES },
    ],
  },
  proveedores: {
    title: "Proveedores",
    description: "Controla red de suministros, contactos clave y soporte para compras.",
    endpoint: "/proveedores",
    singular: "proveedor",
    fields: [
      { name: "nit", label: "NIT", type: "text", required: true },
      { name: "nombre", label: "Nombre", type: "text", required: true },
      { name: "telefono", label: "Teléfono", type: "tel", required: true },
      { name: "correo", label: "Correo", type: "email", required: true },
      { name: "direccion", label: "Dirección", type: "text", required: true },
      { name: "contactoPrincipal", label: "Contacto principal", type: "text", required: true },
      { name: "estado", label: "Estado", type: "select", required: true, options: RECORD_STATUSES },
      { name: "observaciones", label: "Observaciones", type: "textarea" },
    ],
  },
  materiales: {
    title: "Materiales",
    description: "Mantén referencias controladas para presupuestos y compras por proyecto.",
    endpoint: "/materiales",
    singular: "material",
    fields: [
      { name: "codigoMaterial", label: "Código", type: "text", required: true },
      { name: "nombre", label: "Nombre", type: "text", required: true },
      { name: "unidadMedida", label: "Unidad", type: "text", required: true },
      { name: "descripcion", label: "Descripción", type: "textarea" },
      { name: "precioReferencia", label: "Precio referencia", type: "number", required: true, min: 0 },
      { name: "estado", label: "Estado", type: "select", required: true, options: RECORD_STATUSES },
    ],
  },
};