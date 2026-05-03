# 09. API y endpoints

## Consideraciones generales
- Todos los endpoints reales se sirven bajo el prefijo `/api`.
- Salvo `POST /api/auth/login`, el resto de rutas funcionales exige autenticación JWT.
- Los endpoints de listados globales aceptan filtros solo cuando están definidos en el router correspondiente.

## Módulo `auth`

| Método | Endpoint | Propósito | Módulo | Observaciones |
|---|---|---|---|---|
| POST | `/api/auth/login` | autenticar usuario | auth | público |
| GET | `/api/auth/me` | obtener usuario autenticado | auth | requiere JWT |

## Módulo `dashboard`

| Método | Endpoint | Propósito | Módulo | Observaciones |
|---|---|---|---|---|
| GET | `/api/dashboard/summary` | retornar métricas, alertas, saldos, avance y eventos recientes | dashboard | requiere JWT |

## Módulo `clientes`

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/clientes` | listar clientes | requiere JWT |
| POST | `/api/clientes` | crear cliente | requiere JWT |
| PUT | `/api/clientes/{client_id}` | actualizar cliente | requiere JWT |

## Módulo `contratistas`

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/contratistas` | listar contratistas | requiere JWT |
| POST | `/api/contratistas` | crear contratista | requiere JWT |
| PUT | `/api/contratistas/{contratista_id}` | actualizar contratista | requiere JWT |

## Módulo `proveedores`

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/proveedores` | listar proveedores | requiere JWT |
| POST | `/api/proveedores` | crear proveedor | requiere JWT |
| PUT | `/api/proveedores/{proveedor_id}` | actualizar proveedor | requiere JWT |

## Módulo `materiales`

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/materiales` | listar materiales | requiere JWT |
| POST | `/api/materiales` | crear material | requiere JWT |
| PUT | `/api/materiales/{material_id}` | actualizar material | requiere JWT |

## Módulo `proyectos` — agregado raíz

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/proyectos` | listar proyectos | filtros: `q`, `estado`, `clienteId`, `fechaDesde`, `fechaHasta`, `montoMin`, `montoMax` |
| POST | `/api/proyectos` | crear proyecto | requiere JWT |
| GET | `/api/proyectos/{project_id}` | consultar detalle de proyecto | requiere JWT |
| PUT | `/api/proyectos/{project_id}` | actualizar proyecto | requiere JWT |

## Bitácora y reportes

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/proyectos/{project_id}/bitacora` | bitácora de un proyecto | filtros: `fechaDesde`, `fechaHasta`, `tipoEvento`, `usuario` |
| GET | `/api/bitacora` | bitácora global | filtros: `fechaDesde`, `fechaHasta`, `tipoEvento`, `usuario`, `proyectoId` |
| GET | `/api/proyectos/{project_id}/reportes/resumen-cliente.pdf` | PDF resumen de proyecto para cliente | descarga de archivo |
| GET | `/api/proyectos/{project_id}/reportes/pagos-compras.csv` | CSV de pagos y compras | descarga de archivo |
| GET | `/api/proyectos/{project_id}/reportes/contratistas.csv` | CSV de pagos a contratistas | descarga de archivo |

## Seguimientos

| Método | Endpoint | Propósito |
|---|---|---|
| POST | `/api/proyectos/{project_id}/seguimientos` | registrar seguimiento |
| PUT | `/api/proyectos/{project_id}/seguimientos/{tracking_id}` | actualizar seguimiento |
| DELETE | `/api/proyectos/{project_id}/seguimientos/{tracking_id}` | baja lógica de seguimiento |

## Fases

| Método | Endpoint | Propósito |
|---|---|---|
| PUT | `/api/proyectos/{project_id}/fases/{phase_id}` | actualizar fase |
| DELETE | `/api/proyectos/{project_id}/fases/{phase_id}` | baja lógica de fase |

## Pagos del cliente

| Método | Endpoint | Propósito |
|---|---|---|
| POST | `/api/proyectos/{project_id}/pagos` | registrar pago del cliente |
| PUT | `/api/proyectos/{project_id}/pagos/{payment_id}` | actualizar pago |
| DELETE | `/api/proyectos/{project_id}/pagos/{payment_id}` | baja lógica de pago |

## Contratistas embebidos en proyecto

| Método | Endpoint | Propósito |
|---|---|---|
| POST | `/api/proyectos/{project_id}/contratistas` | asignar contratista |
| PUT | `/api/proyectos/{project_id}/contratistas/{assignment_id}` | actualizar asignación |
| DELETE | `/api/proyectos/{project_id}/contratistas/{assignment_id}` | baja lógica de asignación |
| POST | `/api/proyectos/{project_id}/contratistas/{assignment_id}/avances` | registrar avance de contratista |
| POST | `/api/proyectos/{project_id}/contratistas/{assignment_id}/pagos` | registrar pago a contratista |

## Compras

| Método | Endpoint | Propósito |
|---|---|---|
| POST | `/api/proyectos/{project_id}/compras` | registrar compra |
| PUT | `/api/proyectos/{project_id}/compras/{purchase_id}` | actualizar compra |
| DELETE | `/api/proyectos/{project_id}/compras/{purchase_id}` | baja lógica de compra |

## Documentos

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| POST | `/api/proyectos/{project_id}/documentos/url` | registrar documento por URL | requiere body JSON |
| PUT | `/api/proyectos/{project_id}/documentos/{document_id}` | actualizar documento | requiere body JSON |
| DELETE | `/api/proyectos/{project_id}/documentos/{document_id}` | baja lógica de documento | requiere motivo |
| POST | `/api/proyectos/{project_id}/documentos/upload` | cargar archivo físico | usa `multipart/form-data` |

## Feeds transversales

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/pagos` | feed global de pagos | filtros: `q`, `estado`, `clienteId`, `fechaDesde`, `fechaHasta`, `montoMin`, `montoMax` |
| GET | `/api/compras` | feed global de compras | mismos filtros del feed de pagos |
| GET | `/api/documentos` | feed global de documentos y evidencias activas | mismos filtros del feed de pagos |

## Archivos cargados

| Método | Endpoint | Propósito | Observaciones |
|---|---|---|---|
| GET | `/api/files/{file_name}` | servir archivo cargado | requiere JWT, responde 404 si no existe |

## Observación de cobertura
No se documentan endpoints no existentes, como eliminación física de catálogos independientes o recuperación de contraseña, porque no están implementados en el router actual.