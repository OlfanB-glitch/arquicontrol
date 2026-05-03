# 02. Alcance del sistema

## Alcance funcional real
ArquiControl cubre actualmente las siguientes capacidades funcionales verificables en código y rutas activas:

- autenticación de usuario administrador con JWT;
- gestión de catálogos operativos: clientes, contratistas, proveedores y materiales;
- creación, consulta, edición y filtrado de proyectos;
- gestión embebida dentro del proyecto de:
  - fases,
  - seguimientos,
  - pagos del cliente,
  - asignaciones de contratistas,
  - avances de contratista,
  - pagos a contratistas,
  - compras,
  - documentos por URL,
  - documentos por carga de archivo;
- bitácora por proyecto y bitácora global con filtros;
- dashboard con métricas, alertas y vistas resumidas;
- reportes básicos por proyecto en PDF y CSV.

## Qué cubre ArquiControl
El sistema cubre el control administrativo y técnico de un portafolio pequeño de proyectos de arquitectura, enfocado en consolidar:

- estado del proyecto,
- avance general,
- pagos del cliente,
- compras y costos,
- pagos a contratistas,
- evidencia documental,
- trazabilidad operativa.

## Qué queda fuera del alcance actual
De acuerdo con la implementación real, quedan fuera del alcance actual:

- gestión multiusuario avanzada con permisos diferenciados;
- aprobación formal de flujos por roles;
- firma electrónica o versionado documental avanzado;
- notificaciones externas por correo, SMS o integraciones de terceros;
- tablero analítico histórico avanzado;
- reportes Excel nativos distintos de CSV;
- módulo independiente de facturación tributaria;
- eliminación física controlada de registros.

## Límites de la versión implementada
- La autenticación opera con un único flujo JWT y usuario seed inicial.
- Los catálogos independientes (clientes, contratistas, proveedores, materiales) cuentan con listar/crear/actualizar; no exponen eliminación por API.
- La baja lógica aplica a subregistros del agregado `proyectos`, no a colecciones maestras independientes.
- La bitácora documenta eventos operativos del módulo proyectos; no existe un módulo de auditoría transversal para login o catálogos independientes.
- Los reportes disponibles son básicos y utilitarios, no plantillas ejecutivas avanzadas.