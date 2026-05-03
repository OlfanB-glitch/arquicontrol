# 04. Casos de uso del sistema

## Actor identificado
De acuerdo con el estado real del sistema, el actor explícito es el **usuario autenticado del estudio** (seed inicial con rol `ARQUITECTA_ADMIN`). No se documentan actores adicionales porque no existen flujos diferenciados por rol en la implementación actual.

## CU-01. Autenticarse en el sistema
- **Actor:** usuario autenticado del estudio.
- **Propósito:** ingresar al panel principal.
- **Flujo básico:**
  1. El usuario accede a la pantalla de login.
  2. Ingresa correo y contraseña.
  3. El frontend envía credenciales a `/api/auth/login`.
  4. El backend valida usuario y contraseña.
  5. El sistema retorna token JWT y datos sanitizados del usuario.
  6. El frontend persiste la sesión y redirige al dashboard.

## CU-02. Gestionar clientes
- **Actor:** usuario autenticado.
- **Propósito:** mantener la base de clientes.
- **Flujo básico:** listar clientes, abrir formulario, crear o actualizar registro y refrescar tabla.

## CU-03. Gestionar proyectos
- **Actor:** usuario autenticado.
- **Propósito:** crear, consultar, filtrar y actualizar proyectos.
- **Flujo básico:**
  1. El usuario ingresa al módulo Proyectos.
  2. Consulta métricas y tabla del portafolio.
  3. Aplica filtros por texto, estado, cliente, fechas y monto.
  4. Crea o actualiza un proyecto.
  5. Accede al detalle del proyecto para operar subregistros.

## CU-04. Registrar seguimientos
- **Actor:** usuario autenticado.
- **Propósito:** documentar avances del proyecto por fase.
- **Flujo básico:**
  1. El usuario abre el detalle del proyecto.
  2. Registra un seguimiento asociado a una fase.
  3. Puede incluir evidencias por URL.
  4. El sistema recalcula avance, indicadores, resumen financiero y bitácora.

## CU-05. Gestionar pagos
- **Actor:** usuario autenticado.
- **Propósito:** registrar pagos del cliente y consultar flujo financiero transversal.
- **Flujo básico:**
  1. El usuario registra un pago desde el detalle del proyecto.
  2. El sistema valida el tipo de pago y la fase cuando aplica.
  3. El resumen financiero se recalcula.
  4. El pago queda disponible en el feed global de pagos.

## CU-06. Gestionar contratistas
- **Actor:** usuario autenticado.
- **Propósito:** asignar contratistas a proyectos y registrar sus avances/pagos.
- **Flujo básico:**
  1. El usuario asigna un contratista a un proyecto.
  2. Registra avances de trabajo.
  3. Registra pagos al contratista.
  4. El sistema actualiza costos ejecutados y trazabilidad.

## CU-07. Gestionar compras
- **Actor:** usuario autenticado.
- **Propósito:** registrar compras por proyecto con detalle de materiales.
- **Flujo básico:**
  1. El usuario registra la compra, proveedor, factura e ítems.
  2. El backend valida proveedor y materiales.
  3. El sistema calcula subtotal, impuesto y total.
  4. La compra impacta el costo ejecutado y queda visible en el feed global.

## CU-08. Gestionar documentos
- **Actor:** usuario autenticado.
- **Propósito:** conservar enlaces y archivos asociados al proyecto.
- **Flujo básico:**
  1. El usuario registra un documento por URL o carga un archivo.
  2. Si es archivo, el backend valida tipo y tamaño.
  3. El documento queda asociado al proyecto o a un seguimiento específico.
  4. El sistema permite abrirlo desde la interfaz.

## CU-09. Consultar bitácora
- **Actor:** usuario autenticado.
- **Propósito:** revisar la trazabilidad operativa.
- **Flujo básico:**
  1. El usuario consulta la bitácora global desde el sidebar o la auditoría por proyecto.
  2. Aplica filtros por fecha, tipo de evento, usuario y proyecto (en módulo global).
  3. Expande un evento para revisar detalle, motivo y resumen del cambio.

## CU-10. Ejecutar baja lógica
- **Actor:** usuario autenticado.
- **Propósito:** desactivar subregistros sin eliminar trazabilidad.
- **Flujo básico:**
  1. El usuario acciona la baja lógica desde el detalle del proyecto.
  2. El sistema abre un modal formal.
  3. El usuario debe ingresar un motivo obligatorio.
  4. El backend persiste la baja lógica y el motivo.
  5. Se registra evento en bitácora.

## CU-11. Exportar reportes
- **Actor:** usuario autenticado.
- **Propósito:** obtener salidas documentales para revisión o entrega.
- **Flujo básico:**
  1. El usuario abre el detalle del proyecto.
  2. Selecciona uno de los reportes disponibles.
  3. El sistema descarga el PDF o CSV correspondiente.

## Observación metodológica
Los casos de uso anteriores describen únicamente flujos comprobables en el código y la interfaz actual. No se documentan procesos como recuperación de contraseña, multiusuario avanzado o aprobaciones por rol porque no están implementados.