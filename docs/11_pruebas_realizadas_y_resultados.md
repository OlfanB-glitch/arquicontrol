# 11. Pruebas realizadas y resultados

## Tipos de pruebas ejecutadas
La evidencia disponible en el proyecto permite documentar tres grupos de validación:

1. **pruebas backend automatizadas** con `pytest` y `requests`;
2. **pruebas visuales/smoke** sobre la URL pública del sistema;
3. **pruebas automatizadas de agentes** registradas en `test_reports/`.

## Pruebas backend

### Suites identificadas
- `backend/tests/test_arquicontrol_api.py`
- `backend/tests/test_observer_traceability.py`

### Cobertura observable
Las pruebas backend ejercitan, entre otros, los siguientes flujos:

- login y resolución de usuario autenticado;
- estructura del dashboard;
- consulta de catálogos seed;
- carga de detalle de proyecto;
- registro de seguimiento;
- registro y edición de pagos;
- asignación de contratistas;
- registro de avances y pagos a contratistas;
- registro, edición y baja lógica de compras;
- registro y gestión documental;
- filtros y feeds globales;
- trazabilidad del patrón Observer;
- API global de bitácora;
- exportación de reportes PDF/CSV;
- validación de motivo obligatorio en baja lógica.

### Resultado documentado
La ejecución más reciente documentada y reproducida arrojó:

- **24 pruebas backend aprobadas**.

## Pruebas visuales o smoke tests
Se documentaron smoke tests sobre la interfaz para validar:

- login;
- navegación lateral;
- dashboard;
- módulo de bitácora;
- detalle del proyecto;
- pestaña de auditoría;
- apertura de modal de baja lógica;
- visibilidad de acciones de reportes.

## Resultados de reportes automáticos

### `test_reports/iteration_2.json`
- backend: 100%
- frontend: 90%
- incidencia crítica detectada: cancelar el prompt de baja lógica seguía disparando la eliminación.

### Corrección posterior
La incidencia fue resuelta reemplazando el prompt por un modal formal y reforzando la validación backend del motivo.

### `test_reports/iteration_3.json`
El reporte documenta:

- backend: 100%
- frontend: 100%
- bitácora global: PASS
- bitácora en dashboard: PASS
- auditoría por proyecto: PASS
- modal formal de baja lógica: PASS
- persistencia del motivo: PASS
- reportes PDF/CSV: PASS

## Incidencias corregidas importantes

### 1. Baja lógica accidental al cancelar prompt
- **Detección:** `iteration_2.json`
- **Problema:** un `window.prompt` cancelado seguía enviando la petición DELETE.
- **Corrección:** sustitución por `LogicalDeleteDialog` y validación explícita del motivo.

### 2. Validación backend del motivo de baja lógica
- **Problema:** el frontend ya exigía motivo, pero el backend aceptaba entradas vacías o ambiguas.
- **Corrección:** `DeleteEmbeddedRequest` ahora exige motivo no vacío y recortado.

## Estado final de pruebas
Con base en la evidencia actual del repositorio:

- backend funcional validado;
- interfaz principal validada mediante smoke y agente frontend;
- reportes básicos validados;
- no se documentan APIs mockeadas.

## Observación metodológica
Existe un reporte previo con un warning menor de desarrollo en `AuditLogPage`, pero el código fue ajustado posteriormente y no se registró una nueva incidencia funcional sobre ese punto.