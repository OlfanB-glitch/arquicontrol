# 10. Validaciones y reglas de negocio

## Validaciones implementadas

## 1. Validaciones de autenticación
- correo con formato válido (`EmailStr`);
- contraseña mínima de 8 caracteres en `LoginRequest`;
- rechazo de credenciales inválidas con `401`.

## 2. Validaciones de catálogos independientes

### Clientes
- documento mínimo de 4 caracteres;
- nombre mínimo de 3 caracteres;
- teléfono mínimo de 7 caracteres;
- correo válido;
- unicidad por `numeroDocumento` en servicio.

### Contratistas
- validaciones equivalentes a cliente más `tarifaBase >= 0`;
- unicidad por `numeroDocumento`.

### Proveedores
- `nit` mínimo de 5 caracteres;
- correo válido;
- unicidad por NIT.

### Materiales
- `codigoMaterial` mínimo de 3 caracteres;
- precio de referencia no negativo;
- unicidad por código.

## 3. Validaciones del proyecto y subregistros

### Proyecto
- código, nombre, descripción y ubicación con longitud mínima;
- `presupuestoEstimado >= 0`;
- `valorContrato >= 0`;
- validación de existencia de `clienteId`;
- validación de orden de fechas del proyecto y de cada fase;
- unicidad de `codigoProyecto`.

### Fases
- porcentajes entre 0 y 100;
- validación de fechas;
- restricción para no eliminar fase con seguimientos o pagos activos asociados.

### Seguimientos
- `faseId` obligatorio;
- observaciones mínimas;
- porcentaje entre 0 y 100;
- la fase indicada debe existir y estar activa.

### Pagos
- monto no negativo;
- concepto mínimo de 3 caracteres;
- `faseId` obligatorio cuando el tipo es `PAGO_POR_FASE`;
- validación de fase existente cuando se referencia.

### Asignaciones de contratista
- contratista referenciado debe existir;
- rol mínimo de 3 caracteres;
- valor acordado no negativo;
- fecha inicial no puede ser posterior a la final.

### Avances y pagos de contratista
- avance con descripción mínima, horas no negativas y porcentaje entre 0 y 100;
- pago con monto no negativo.

### Compras
- proveedor debe existir;
- la compra debe tener al menos un detalle;
- cada material referenciado debe existir;
- cantidad de detalle > 0;
- precio unitario >= 0;
- impuesto >= 0.

### Documentos
- nombre, tipo y URL con longitud mínima;
- validación de seguimiento si el documento se asocia a uno;
- carga de archivo obligatoria en uploads;
- extensiones permitidas: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.docx`, `.xlsx`, `.txt`, `.md`;
- tamaño máximo: 10 MB;
- rechazo de archivo vacío.

## Reglas de negocio críticas

## 1. Consistencia del resumen financiero
Cada modificación relevante del agregado `Proyecto` ejecuta `_recalculate_project()` y actualiza:

- `totalPagadoCliente`
- `saldoPendienteCliente`
- `totalCompras`
- `totalPagadoContratistas`
- `costoTotalEjecutado`
- `margenEstimado`

La consistencia financiera no depende del frontend; se recalcula en backend.

## 2. Consistencia del avance general
El avance general depende de una estrategia:

- por seguimientos;
- por fases.

La estrategia se resuelve con `AvanceStrategyResolver` según `metodoCalculoAvance`.

## 3. Baja lógica con motivo obligatorio
La baja lógica de fases, seguimientos, pagos, asignaciones, compras y documentos exige un `motivo` no vacío. El backend lo valida con `DeleteEmbeddedRequest` y persiste:

- `isActive = false`
- `deletedAt`
- `deletedBy`
- `motivo`
- `updatedAt`

## 4. Restricción de cierre de proyecto
Un proyecto no puede marcarse como `FINALIZADO` o `ENTREGADO` si conserva un saldo pendiente importante. La regla actual impide el cierre cuando el saldo es mayor que `max(valorContrato * 0.1, 1)`.

## 5. Restricciones de eliminación lógica
- una fase no puede darse de baja si tiene seguimientos o pagos activos;
- una asignación de contratista no puede darse de baja si ya tiene avances o pagos registrados.

## 6. Bitácora e indicadores automáticos
Cada operación relevante del agregado dispara eventos Observer que actualizan:

- `bitacora`
- `indicadores`
- `alertas`

## Restricciones importantes del sistema
- no existe eliminación física de subregistros operativos;
- los feeds globales muestran únicamente registros activos;
- la serialización del proyecto, por defecto, excluye elementos inactivos;
- la bitácora por proyecto conserva los eventos más recientes gestionados por el observer.