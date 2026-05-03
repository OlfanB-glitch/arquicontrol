# 14. Guion de demostración y sustentación

## Objetivo del guion
Presentar ArquiControl en una demostración académica de 5 a 10 minutos, resaltando problema, solución, arquitectura, modelo documental, patrones de diseño y funcionalidades reales implementadas.

## Orden recomendado para la demo

1. **Login**
2. **Dashboard**
3. **Clientes**
4. **Proyectos**
5. **Detalle de proyecto**
6. **Bitácora global**
7. **Reportes**
8. **Cierre técnico**

## Flujo de demostración sugerido

## Minuto 1: Presentación del problema
Explique que el arquitecto independiente suele manejar información dispersa entre archivos, hojas de cálculo y mensajería, lo que dificulta el control operativo, financiero y documental.

## Minuto 2: Login y acceso al sistema
Muestre el login y comente que el sistema trabaja con autenticación real por JWT y usuario persistido en MongoDB.

## Minuto 3: Dashboard
Explique que el dashboard resume:
- portafolio por estado,
- alertas automáticas,
- saldo pendiente,
- avance consolidado,
- bitácora reciente,
- pagos y compras recientes.

## Minuto 4: Gestión de catálogos
Abra uno de los módulos de catálogo (por ejemplo, Clientes o Contratistas) y explique que estos módulos centralizan la base operativa del estudio.

## Minuto 5 y 6: Proyectos como agregado raíz
Abra el módulo **Proyectos** y luego el detalle de un proyecto.

En esta parte conviene justificar que:
- `proyectos` es el agregado raíz;
- fases, seguimientos, pagos, compras y documentos son subdocumentos embebidos;
- el proyecto concentra el estado operativo completo.

## Minuto 6 y 7: Operación interna del proyecto
Recorra las pestañas del detalle del proyecto y explique que desde allí se gestiona:
- seguimiento técnico,
- pagos del cliente,
- contratistas,
- compras,
- documentos.

## Minuto 7: Bitácora y baja lógica
Abra la pestaña **Auditoría** o el módulo **Bitácora**.

### Qué explicar
- cada evento registra fecha, usuario, proyecto, tipo, subregistro, acción y motivo;
- las bajas no son físicas, sino lógicas;
- el motivo es obligatorio;
- esto mejora trazabilidad y defendibilidad de cambios.

## Minuto 8: Reportes
Muestre la sección de reportes del detalle del proyecto y explique que la versión actual genera:
- un PDF de resumen para cliente;
- CSV de pagos y compras;
- CSV de pagos a contratistas.

## Cómo justificar MongoDB
- el proyecto concentra información jerárquica y cambiante;
- el agregado `Proyecto` contiene subestructuras fuertemente relacionadas;
- el modelo documental reduce joins y favorece lectura integral del proyecto.

## Cómo justificar la arquitectura
- se implementó un monolito modular porque el dominio requería separación clara sin la complejidad operativa de microservicios;
- cada módulo backend tiene capas de presentation, application, domain e infrastructure;
- esto facilita trazabilidad académica y mantenimiento.

## Cómo justificar los patrones de diseño
- **Repository:** desacopla acceso a datos;
- **Singleton:** centraliza conexión a MongoDB;
- **Strategy:** cambia la forma de calcular avance del proyecto;
- **Factory Method:** normaliza creación de pagos por tipo;
- **Observer:** actualiza bitácora, indicadores y alertas tras cada evento.

## Cómo justificar la bitácora y la baja lógica
- la bitácora garantiza trazabilidad operativa;
- la baja lógica evita pérdida total de información;
- el motivo obligatorio fortalece el control administrativo y la auditoría.

## Cierre sugerido
Concluya indicando que ArquiControl ya resuelve el núcleo del problema operativo del arquitecto independiente, manteniendo consistencia documental y financiera dentro de una arquitectura académicamente defendible.