# 03. Requerimientos funcionales y no funcionales

## Requerimientos funcionales cubiertos

### RF-01. Autenticación
El sistema debe permitir autenticación mediante correo y contraseña. **Cubierto** por `/api/auth/login`, `/api/auth/me` y el contexto `useAuth` en frontend.

### RF-02. Gestión de clientes
El sistema debe permitir listar, crear y actualizar clientes. **Cubierto** por el módulo `clientes`.

### RF-03. Gestión de contratistas
El sistema debe permitir listar, crear y actualizar contratistas. **Cubierto** por el módulo `contratistas`.

### RF-04. Gestión de proveedores
El sistema debe permitir listar, crear y actualizar proveedores. **Cubierto** por el módulo `proveedores`.

### RF-05. Gestión de materiales
El sistema debe permitir listar, crear y actualizar materiales. **Cubierto** por el módulo `materiales`.

### RF-06. Gestión de proyectos
El sistema debe permitir listar, filtrar, crear, consultar y actualizar proyectos. **Cubierto** por el módulo `proyectos`.

### RF-07. Gestión de fases
El sistema debe permitir editar y dar de baja lógica fases embebidas. **Cubierto** por endpoints `PUT` y `DELETE` sobre `/proyectos/{id}/fases/{fase_id}`.

### RF-08. Gestión de seguimientos
El sistema debe permitir registrar, actualizar y dar de baja lógica seguimientos con evidencias. **Cubierto**.

### RF-09. Gestión de pagos del cliente
El sistema debe permitir registrar, actualizar y dar de baja lógica pagos. **Cubierto**.

### RF-10. Gestión de contratistas asignados
El sistema debe permitir asignar contratistas, actualizar asignaciones, registrar avances y pagos, y ejecutar baja lógica de asignaciones cuando la regla de negocio lo permita. **Cubierto**.

### RF-11. Gestión de compras
El sistema debe permitir registrar, actualizar y dar de baja lógica compras con detalle de materiales. **Cubierto**.

### RF-12. Gestión documental
El sistema debe permitir asociar documentos por URL y cargar archivos reales. **Cubierto**.

### RF-13. Auditoría operativa
El sistema debe permitir consultar bitácora por proyecto y bitácora global con filtros. **Cubierto**.

### RF-14. Reportes básicos
El sistema debe permitir exportar un PDF de resumen para cliente y CSV operativos por proyecto. **Cubierto**.

## Requerimientos no funcionales observables

### RNF-01. Modularidad
El backend está organizado por módulos de dominio y capas explícitas. **Observable** en `backend/app/modules/*`.

### RNF-02. Trazabilidad
Las operaciones del agregado `proyectos` generan bitácora e indicadores por patrón Observer. **Observable** en `observers.py` y `service.py`.

### RNF-03. Consistencia de datos
El resumen financiero y el avance general se recalculan automáticamente tras mutaciones del proyecto. **Observable** en `_recalculate_project()`.

### RNF-04. Validación de entrada
Los modelos Pydantic imponen restricciones de formato, obligatoriedad y rangos numéricos. **Observable** en `domain/models.py`.

### RNF-05. Seguridad básica
Los endpoints protegidos exigen JWT válido y el backend sanitiza la respuesta del usuario autenticado. **Observable** en `auth/application/service.py`.

### RNF-06. Persistencia documental
La información operativa se persiste en MongoDB con estructura documental. **Observable** en el diseño del agregado `Proyecto`.

### RNF-07. Usabilidad operativa
El frontend expone navegación lateral, formularios por módulo, filtros y estados visibles. **Observable** en `Sidebar.js`, `EntityPage.js`, `ProjectsPage.js`, `ProjectDetailPage.js`, `AuditLogPage.js` y `DashboardPage.js`.

### RNF-08. Verificabilidad
El proyecto cuenta con pruebas backend automatizadas y evidencia de validación visual/smoke. **Observable** en `backend/tests/` y `test_reports/`.