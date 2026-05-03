# 05. Modelo de datos no relacional

## Fundamentación: por qué la base de datos es no relacional
ArquiControl utiliza MongoDB y organiza su información con un enfoque documental. La decisión es coherente con el dominio implementado porque el proyecto concentra múltiples elementos estrechamente relacionados que cambian de forma conjunta: fases, seguimientos, pagos, compras, documentos y contratistas asignados. En este contexto, un modelo documental reduce la fragmentación y favorece la lectura integral del estado operativo del proyecto.

## Colecciones reales
Las colecciones verificadas en el código y en el seed son:

- `usuarios`
- `clientes`
- `contratistas`
- `proveedores`
- `materiales`
- `proyectos`

## `proyectos` como agregado raíz
La colección `proyectos` actúa como agregado raíz porque encapsula:

- el ciclo de vida del proyecto;
- el avance general;
- el resumen financiero;
- la bitácora operativa;
- alertas e indicadores;
- los subdocumentos operativos que deben mantenerse consistentes entre sí.

Esto se confirma en `ProyectoResponse` y en `ProyectoService`, donde la lógica de recálculo y validación se aplica sobre el documento completo.

## Subdocumentos embebidos en `proyectos`
De acuerdo con `backend/app/modules/proyectos/domain/models.py`, los subdocumentos embebidos reales son:

- `fases[]`
- `seguimientos[]`
  - `evidencias[]` dentro de cada seguimiento
- `pagos[]`
- `contratistasAsignados[]`
  - `avances[]`
  - `pagosContratista[]`
- `compras[]`
  - `detalleCompra[]`
- `documentos[]`
- `resumenFinanciero`
- `bitacora[]`
- `alertas[]`
- `indicadores`

## Entidades referenciadas
Aunque el proyecto embebe gran parte de la operación, existen referencias hacia colecciones maestras:

- `clienteId` referencia a `clientes`
- `contratistaId` dentro de asignaciones referencia a `contratistas`
- `proveedorId` dentro de compras referencia a `proveedores`
- `materialId` dentro de detalles de compra referencia a `materiales`

Estas referencias se validan en tiempo de aplicación dentro de `ProyectoService`.

## Ejemplo simplificado de documento `proyectos`
```json
{
  "id": "proy-001",
  "codigoProyecto": "ARQ-001",
  "clienteId": "cli-001",
  "nombreProyecto": "Casa Patio Nogal",
  "tipoProyecto": "VIVIENDA",
  "estadoProyecto": "EN_EJECUCION",
  "fases": [
    {
      "id": "fase-001",
      "nombre": "Anteproyecto",
      "porcentajeAvance": 100,
      "isActive": true
    }
  ],
  "seguimientos": [
    {
      "id": "seg-001",
      "faseId": "fase-002",
      "observaciones": "Coordinación resuelta",
      "evidencias": [
        {
          "id": "evi-001",
          "nombre": "Comité técnico abril",
          "url": "https://...",
          "fuente": "URL"
        }
      ]
    }
  ],
  "pagos": [
    {
      "idPago": "pag-001",
      "tipoPago": "ANTICIPO",
      "monto": 60000000,
      "isActive": true
    }
  ],
  "compras": [],
  "documentos": [],
  "resumenFinanciero": {
    "totalPagadoCliente": 0,
    "saldoPendienteCliente": 0,
    "totalCompras": 0,
    "totalPagadoContratistas": 0,
    "costoTotalEjecutado": 0,
    "margenEstimado": 0
  },
  "bitacora": [],
  "alertas": [],
  "indicadores": {}
}
```

## Validaciones relevantes del modelo documental
- campos obligatorios y mínimos de longitud con Pydantic;
- montos no negativos (`ge=0`);
- porcentajes entre 0 y 100;
- compras con al menos un detalle;
- pagos por fase con `faseId` obligatorio;
- motivo obligatorio para baja lógica;
- metadatos de ciclo de vida (`isActive`, `deletedAt`, `deletedBy`, `motivo`, `updatedAt`).

## Índices definidos

ArquiControl define índices explícitos en `backend/app/core/indexes.py` que se aplican durante el evento `startup` del backend mediante `ensure_indexes()`. Los índices cumplen dos funciones:

1. **Rendimiento:** aceleran consultas frecuentes de búsqueda, filtro y ordenamiento.
2. **Integridad:** los índices únicos previenen race conditions que la validación en capa de servicio no puede cubrir.

### Tabla de índices por colección

| Colección | Campo | Tipo | Justificación |
|---|---|---|---|
| `usuarios` | `email` | único | login busca por correo; garantiza una sola cuenta por email |
| `usuarios` | `id` | único | resolución del usuario tras validar JWT |
| `clientes` | `numeroDocumento` | único | regla de negocio: un cliente = un documento |
| `clientes` | `id` | único | referenciado desde `proyectos.clienteId` |
| `clientes` | `nombreCompleto` | ascendente | ordenamiento en `list_all()` |
| `contratistas` | `numeroDocumento` | único | regla de negocio |
| `contratistas` | `id` | único | referenciado desde asignaciones de contratista |
| `contratistas` | `nombreCompleto` | ascendente | ordenamiento |
| `proveedores` | `nit` | único | regla de negocio: un proveedor = un NIT |
| `proveedores` | `id` | único | referenciado desde compras |
| `proveedores` | `nombre` | ascendente | ordenamiento |
| `materiales` | `codigoMaterial` | único | regla de negocio |
| `materiales` | `id` | único | referenciado desde detalle de compra |
| `materiales` | `nombre` | ascendente | ordenamiento |
| `proyectos` | `codigoProyecto` | único | regla de negocio |
| `proyectos` | `id` | único | búsqueda por ID |
| `proyectos` | `clienteId` | ascendente | filtro por cliente en listados |
| `proyectos` | `estadoProyecto` | ascendente | filtro por estado |
| `proyectos` | `updatedAt` | descendente | ordenamiento por última actualización |

### Consideración técnica
`create_index()` es idempotente en MongoDB: invocarlo varias veces sobre el mismo índice no genera duplicados ni errores, lo que permite ejecutarlo en cada arranque sin impacto en el rendimiento.

## Observación académica
El modelo documental no elimina la necesidad de consistencia; simplemente la desplaza hacia reglas de dominio y servicios de aplicación. En ArquiControl, esa consistencia se garantiza mediante validaciones de servicio, recálculos automáticos y patrones como Observer y Strategy.