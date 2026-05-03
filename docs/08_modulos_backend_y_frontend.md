# 08. Módulos backend y frontend

## Módulos backend reales

### 1. `auth`
**Responsabilidad:** autenticación por JWT y resolución del usuario autenticado.

**Capas observadas:**
- `domain/models.py`
- `application/service.py`
- `infrastructure/repository.py`
- `presentation/router.py`

**Relación con frontend:** `LoginPage.js` y `useAuth.js`.

### 2. `clientes`
**Responsabilidad:** listar, crear y actualizar clientes.

**Capas observadas:**
- `domain/models.py`, `domain/repositories.py`
- `application/service.py`
- `infrastructure/repository.py`
- `presentation/router.py`

**Relación con frontend:** `EntityPage.js` con configuración `entityModules.clientes`.

### 3. `contratistas`
**Responsabilidad:** administrar contratistas independientes.

**Relación con frontend:** `EntityPage.js` con `entityModules.contratistas` y formularios embebidos en `ProjectDetailPage.js`.

### 4. `proveedores`
**Responsabilidad:** administrar proveedores de suministros.

**Relación con frontend:** `EntityPage.js` con `entityModules.proveedores` y selección en compras del detalle del proyecto.

### 5. `materiales`
**Responsabilidad:** administrar catálogo de materiales.

**Relación con frontend:** `EntityPage.js` con `entityModules.materiales` y uso en detalles de compra.

### 6. `proyectos`
**Responsabilidad:** núcleo funcional del sistema. Gestiona el agregado raíz `Proyecto`, subdocumentos embebidos, bitácora, feeds y reportes.

**Capas observadas:**
- `domain/models.py`
- `domain/repositories.py`
- `domain/strategies.py`
- `domain/payment_factories.py`
- `domain/observers.py`
- `application/service.py`
- `infrastructure/repository.py`
- `presentation/router.py`

**Relación con frontend:** `ProjectsPage.js`, `ProjectDetailPage.js`, `FeedPage.js`, `AuditLogPage.js`.

### 7. `dashboard`
**Responsabilidad:** consolidar métricas, alertas, saldos, avance y eventos recientes.

**Relación con frontend:** `DashboardPage.js`.

## Responsabilidades por módulo

| Módulo | Responsabilidad principal |
|---|---|
| auth | sesión y control de acceso |
| clientes | catálogo de clientes |
| contratistas | catálogo de contratistas |
| proveedores | catálogo de proveedores |
| materiales | catálogo de materiales |
| proyectos | agregado raíz, operación, auditoría y reportes |
| dashboard | resumen ejecutivo del sistema |

## Páginas o secciones frontend reales

| Página / sección | Archivo | Función |
|---|---|---|
| Login | `frontend/src/pages/LoginPage.js` | autenticación |
| Dashboard | `DashboardPage.js` | métricas, alertas, bitácora reciente |
| Clientes | `EntityPage.js` | CRUD básico de clientes |
| Contratistas | `EntityPage.js` | CRUD básico de contratistas |
| Proveedores | `EntityPage.js` | CRUD básico de proveedores |
| Materiales | `EntityPage.js` | CRUD básico de materiales |
| Proyectos | `ProjectsPage.js` | listado, filtros, métricas y alta/edición |
| Detalle de proyecto | `ProjectDetailPage.js` | operación embebida del agregado |
| Bitácora | `AuditLogPage.js` | auditoría global filtrable |
| Pagos | `FeedPage.js` | feed transversal de pagos |
| Compras | `FeedPage.js` | feed transversal de compras |
| Documentos | `FeedPage.js` | feed transversal de documentos |

## Relación entre frontend y backend

| Frontend | Backend relacionado |
|---|---|
| `LoginPage.js` | `auth` |
| `DashboardPage.js` | `dashboard`, `proyectos` |
| `EntityPage.js` | `clientes`, `contratistas`, `proveedores`, `materiales` |
| `ProjectsPage.js` | `proyectos` |
| `ProjectDetailPage.js` | `proyectos` |
| `AuditLogPage.js` | `proyectos` (bitácora global) |
| `FeedPage.js` | feeds de `proyectos` (`/pagos`, `/compras`, `/documentos`) |

## Observación de consistencia
No existe un frontend separado por carpetas de dominio; la separación en frontend se da principalmente por páginas y componentes reutilizables. La separación estricta por dominio se concentra sobre todo en el backend.