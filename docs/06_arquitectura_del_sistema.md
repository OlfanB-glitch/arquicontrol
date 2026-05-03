# 06. Arquitectura del sistema

## Estilo arquitectónico real
ArquiControl está implementado como un **monolito modular**. Esta decisión puede verificarse en la estructura del backend, donde todos los módulos comparten la misma aplicación FastAPI, pero se separan por dominio y capas.

## Organización modular por dominio
La estructura real del backend se organiza así:

```text
backend/app
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── modules/
│   ├── auth/
│   ├── clientes/
│   ├── contratistas/
│   ├── dashboard/
│   ├── materiales/
│   ├── proveedores/
│   └── proyectos/
├── seed/
└── shared/
```

## Capas existentes
Cada módulo principal sigue, de forma explícita, las capas:

- **presentation:** define routers HTTP y contratos de entrada/salida.
- **application:** contiene servicios y casos de uso.
- **domain:** define modelos, interfaces y patrones de diseño.
- **infrastructure:** implementa acceso a MongoDB.

El módulo `dashboard` es más liviano, pero sigue la misma orientación modular.

## Flujo entre frontend, backend y MongoDB

1. El usuario interactúa con el frontend React.
2. El frontend consume el backend vía Axios usando `REACT_APP_BACKEND_URL/api`.
3. FastAPI resuelve autenticación, validaciones y lógica de aplicación.
4. Los repositorios acceden a MongoDB mediante Motor.
5. El servicio transforma, recalcula y serializa el estado final.
6. El frontend renderiza tablas, formularios, feeds, bitácora y reportes.

## Arquitectura del frontend
El frontend real se compone de:

- enrutamiento protegido con React Router;
- `AuthProvider` para mantener la sesión;
- `AppShell` y `Sidebar` para navegación persistente;
- páginas especializadas (`DashboardPage`, `ProjectsPage`, `ProjectDetailPage`, `AuditLogPage`, `EntityPage`, `FeedPage`, `LoginPage`);
- componentes reutilizables para tablas, formularios, métricas, auditoría y modales.

## Manejo de archivos
El sistema gestiona archivos de dos formas:

- **documentos por URL**, que conservan un enlace externo o interno;
- **documentos cargados al servidor**, almacenados físicamente en `UPLOADS_DIR`.

Los archivos cargados se sirven mediante `/api/files/{file_name}` y están protegidos por autenticación.

## Bitácora y reportes dentro de la arquitectura
- La **bitácora** no es un microservicio independiente: forma parte del módulo `proyectos` y se alimenta mediante el patrón Observer.
- Los **reportes** se generan en capa de aplicación del módulo `proyectos` a partir del estado actual del agregado.

## Estructura real de carpetas del frontend
```text
frontend/src
├── components/
├── hooks/
├── lib/
└── pages/
    ├── AuditLogPage.js
    ├── DashboardPage.js
    ├── EntityPage.js
    ├── FeedPage.js
    ├── LoginPage.js
    ├── ProjectDetailPage.js
    └── ProjectsPage.js
```

## Justificación técnica de la organización adoptada
La arquitectura elegida favorece:

- separación clara de responsabilidades;
- trazabilidad entre reglas de negocio y endpoints;
- crecimiento por dominios sin mezclar controladores con lógica central;
- coherencia con el modelo documental basado en agregado raíz.

## Alcance arquitectónico actual
No se observan microservicios, colas, workers ni integraciones externas complejas. Toda la operación se concentra en una única aplicación full-stack con persistencia en MongoDB.