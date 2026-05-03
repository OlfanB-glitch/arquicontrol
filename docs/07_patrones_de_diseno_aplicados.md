# 07. Patrones de diseño aplicados

## Enfoque general
ArquiControl implementa de forma observable los patrones Repository, Singleton, Strategy, Factory Method y Observer. La siguiente descripción se limita a archivos y usos comprobables en el código real.

## 1. Repository

### Propósito
Abstraer el acceso a datos para desacoplar la lógica de aplicación de los detalles de persistencia en MongoDB.

### Por qué se usó en ArquiControl
El sistema maneja múltiples dominios (`clientes`, `contratistas`, `proveedores`, `materiales`, `proyectos`) y necesitaba una capa estable para operaciones CRUD y agregaciones.

### Archivos donde está implementado
- `backend/app/modules/clientes/domain/repositories.py`
- `backend/app/modules/clientes/infrastructure/repository.py`
- `backend/app/modules/contratistas/domain/repositories.py`
- `backend/app/modules/contratistas/infrastructure/repository.py`
- `backend/app/modules/proveedores/domain/repositories.py`
- `backend/app/modules/proveedores/infrastructure/repository.py`
- `backend/app/modules/materiales/domain/repositories.py`
- `backend/app/modules/materiales/infrastructure/repository.py`
- `backend/app/modules/proyectos/domain/repositories.py`
- `backend/app/modules/proyectos/infrastructure/repository.py`

### Beneficio técnico
Permite que los servicios de aplicación trabajen sobre contratos y no sobre consultas incrustadas, facilitando mantenimiento, pruebas y lectura académica del sistema.

## 2. Singleton

### Propósito
Garantizar una única instancia compartida para la conexión a la base de datos.

### Por qué se usó en ArquiControl
MongoDB se consume desde varios módulos, y el sistema evita crear clientes duplicados de Motor en cada operación.

### Archivo exacto
- `backend/app/core/database.py` (`MongoConnection`)

### Beneficio técnico
Centraliza la conexión, simplifica el acceso a la base y reduce el acoplamiento con la infraestructura.

## 3. Strategy

### Propósito
Permitir que el cálculo del avance general del proyecto cambie según una estrategia seleccionada.

### Por qué se usó en ArquiControl
El proyecto puede calcular su avance desde seguimientos o desde fases, dependiendo del valor `metodoCalculoAvance`.

### Archivos exactos
- `backend/app/modules/proyectos/domain/strategies.py`
- Uso en `backend/app/modules/proyectos/application/service.py` (`self.avance_resolver.resolve(...)`)

### Implementaciones reales
- `AvancePorSeguimientosStrategy`
- `AvancePorFasesStrategy`
- `AvanceStrategyResolver`

### Beneficio técnico
Evita condicionales dispersos y deja explícita la política de cálculo del avance.

## 4. Factory Method

### Propósito
Encapsular la creación de pagos según el tipo de pago solicitado.

### Por qué se usó en ArquiControl
Los pagos `ANTICIPO`, `PAGO_POR_FASE` y `PAGO_GENERAL` no se construyen exactamente igual. El tipo de pago determina si se exige fase y cómo se normaliza el registro.

### Archivos exactos
- `backend/app/modules/proyectos/domain/payment_factories.py`
- Uso en `backend/app/modules/proyectos/application/service.py` (`_build_payment_record`)

### Implementaciones reales
- `AnticipoFactory`
- `PagoPorFaseFactory`
- `PagoGeneralFactory`
- `PagoFactoryResolver`

### Beneficio técnico
Concentra la lógica de creación y valida coherentemente cada variante del pago.

## 5. Observer

### Propósito
Reaccionar automáticamente a eventos del agregado `proyectos` para mantener bitácora, indicadores y alertas.

### Por qué se usó en ArquiControl
Cada mutación relevante del proyecto debía generar trazabilidad y recalcular información derivada sin replicar lógica en cada endpoint.

### Archivos exactos
- `backend/app/modules/proyectos/domain/observers.py`
- Uso en `backend/app/modules/proyectos/application/service.py` (`self.event_publisher.notify(...)`)

### Observadores reales
- `BitacoraProyectoObserver`
- `IndicadoresProyectoObserver`
- `AlertaPagosObserver`
- `ProyectoEventPublisher`

### Beneficio técnico
Mantiene sincronizadas las consecuencias del evento de dominio: bitácora, indicadores y alertas se actualizan sin duplicar lógica procedural en cada caso de uso.

## Observación académica final
Los patrones no se limitan a una mención teórica; su uso es trazable en archivos concretos y afecta el comportamiento real del sistema. Esto fortalece la defendibilidad académica del proyecto.