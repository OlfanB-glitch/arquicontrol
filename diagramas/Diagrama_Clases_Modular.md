# Diagrama de Clases — Vista Modular

> División del diagrama técnico monolítico en módulos por dominio funcional, más un diagrama dedicado a los patrones de diseño transversales. Cada módulo incluye sus entidades, controladores, servicios e interfaces de repositorio relevantes.

---

## Índice

1. [Módulo 1 — Núcleo del Proyecto](#módulo-1--núcleo-del-proyecto)
2. [Módulo 2 — Gestión de Clientes](#módulo-2--gestión-de-clientes)
3. [Módulo 3 — Contratistas y Asignaciones](#módulo-3--contratistas-y-asignaciones)
4. [Módulo 4 — Pagos del Cliente](#módulo-4--pagos-del-cliente)
5. [Módulo 5 — Compras, Proveedores y Materiales](#módulo-5--compras-proveedores-y-materiales)
6. [Módulo 6 — Seguimiento y Documentos](#módulo-6--seguimiento-y-documentos)
7. [Módulo 7 — Patrones de Diseño (Observer + Strategy)](#módulo-7--patrones-de-diseño-observer--strategy)
8. [Módulo 8 — Infraestructura](#módulo-8--infraestructura)
9. [Mapa general de dependencias entre módulos](#mapa-general-de-dependencias-entre-módulos)

---

## Módulo 1 — Núcleo del Proyecto

Entidad raíz del sistema. Aquí vive `Proyecto` con sus fases y la trinidad Controller → Service → Repository que orquesta las operaciones principales.

```mermaid
classDiagram
    class Proyecto {
        +id: String
        +codigoProyecto: String
        +nombre: String
        +descripcion: String
        +ubicacion: String
        +areaM2: Decimal
        +presupuestoEstimado: Decimal
        +valorContrato: Decimal
        +porcentajeAvanceGeneral: Decimal
        +estadoProyecto: String
        +agregarFase()
        +registrarSeguimiento()
        +registrarPago()
        +asignarContratista()
        +registrarCompra()
        +adjuntarDocumento()
    }

    class FaseProyecto {
        +id: String
        +nombre: String
        +orden: int
        +porcentajePlaneado: Decimal
        +valorPlaneado: Decimal
        +estado: String
    }

    class ProyectoController {
        +crearProyecto()
        +consultarProyecto()
        +editarProyecto()
        +actualizarEstadoProyecto()
        +registrarSeguimiento()
    }

    class ProyectoService {
        +crearProyecto()
        +actualizarProyecto()
        +actualizarEstado()
        +registrarSeguimiento()
        +recalcularAvance()
        +notificarCambioProyecto()
    }

    class IProyectoRepository {
        <<interface>>
        +save(proyecto)
        +findById(id)
        +update(proyecto)
        +findAll()
    }

    class ProyectoRepositoryMongo {
        +save(proyecto)
        +findById(id)
        +update(proyecto)
        +findAll()
    }

    Proyecto "1" *-- "1..*" FaseProyecto : contiene
    ProyectoController --> ProyectoService : usa
    ProyectoService --> IProyectoRepository : usa
    ProyectoRepositoryMongo ..|> IProyectoRepository : implementa
```

---

## Módulo 2 — Gestión de Clientes

Subsistema autónomo para administrar la cartera de clientes. Es referenciado por `Proyecto` (un cliente tiene 1..N proyectos).

```mermaid
classDiagram
    class Cliente {
        +id: String
        +nombreCompleto: String
        +telefono: String
        +correo: String
        +direccion: String
        +ciudad: String
        +estado: String
    }

    class ClienteController {
        +crearCliente()
        +consultarClientes()
        +editarCliente()
    }

    class ClienteService {
        +crearCliente()
        +actualizarCliente()
        +consultarClientes()
    }

    class IClienteRepository {
        <<interface>>
        +save(cliente)
        +findById(id)
        +update(cliente)
        +findAll()
    }

    class ClienteRepositoryMongo {
        +save(cliente)
        +findById(id)
        +update(cliente)
        +findAll()
    }

    ClienteController --> ClienteService : usa
    ClienteService --> IClienteRepository : usa
    ClienteRepositoryMongo ..|> IClienteRepository : implementa
```

> **Relación con Núcleo:** `Proyecto` referencia a `Cliente` mediante `clienteId` (cardinalidad `1..* → 1`).

---

## Módulo 3 — Contratistas y Asignaciones

Gestiona la red de contratistas, su asignación a proyectos, los avances de obra registrados y los pagos por jornadas o concepto.

```mermaid
classDiagram
    class Contratista {
        +id: String
        +nombreCompleto: String
        +especialidad: String
        +telefono: String
        +correo: String
        +tarifaBase: Decimal
        +estado: String
    }

    class AsignacionContratista {
        +id: String
        +rol: String
        +fechaInicio: Date
        +fechaFin: Date
        +valorAcordado: Decimal
        +estado: String
    }

    class AvanceContratista {
        +id: String
        +fechaRegistro: Date
        +horasTrabajadas: Decimal
        +jornadas: int
        +descripcionAvance: String
    }

    class PagoContratista {
        +id: String
        +fechaPago: Date
        +monto: Decimal
        +concepto: String
        +metodoPago: String
    }

    class ContratistaController {
        +registrarContratista()
        +asignarContratistaProyecto()
        +registrarAvanceContratista()
        +registrarPagoContratista()
    }

    class ContratistaService {
        +registrarContratista()
        +asignarAProyecto()
        +registrarAvance()
        +registrarPago()
    }

    class IContratistaRepository {
        <<interface>>
        +save(contratista)
        +findById(id)
        +findAll()
    }

    class ContratistaRepositoryMongo {
        +save(contratista)
        +findById(id)
        +findAll()
    }

    AsignacionContratista "1" --> "1" Contratista : referencia
    AsignacionContratista "1" *-- "0..*" AvanceContratista : registra
    AsignacionContratista "1" *-- "0..*" PagoContratista : genera

    ContratistaController --> ContratistaService : usa
    ContratistaService --> IContratistaRepository : usa
    ContratistaRepositoryMongo ..|> IContratistaRepository : implementa
```

> **Relación con Núcleo:** `Proyecto` contiene `0..*` `AsignacionContratista`.

---

## Módulo 4 — Pagos del Cliente

Subsistema de cobros con **patrón Factory Method** para crear distintos tipos de pago (anticipo, por fase o general).

```mermaid
classDiagram
    class PagoProyecto {
        +id: String
        +tipoPago: TipoPago
        +fechaPago: Date
        +monto: Decimal
        +metodoPago: String
        +referencia: String
        +observaciones: String
    }

    class TipoPago {
        <<enumeration>>
        ANTICIPO
        PAGO_POR_FASE
        PAGO_GENERAL
    }

    class PagoFactory {
        <<abstract>>
        +crearPago(datos) PagoProyecto
    }

    class PagoGeneralFactory {
        +crearPago(datos) PagoProyecto
    }

    class PagoPorFaseFactory {
        +crearPago(datos) PagoProyecto
    }

    class AnticipoFactory {
        +crearPago(datos) PagoProyecto
    }

    class PagoController {
        +registrarPagoProyecto()
        +consultarPagosProyecto()
        +consultarSaldoPendiente()
    }

    class PagoService {
        +registrarPagoProyecto()
        +consultarPagos()
        +calcularSaldoPendiente()
    }

    PagoProyecto --> TipoPago : usa

    PagoFactory <|-- PagoGeneralFactory
    PagoFactory <|-- PagoPorFaseFactory
    PagoFactory <|-- AnticipoFactory

    PagoFactory ..> PagoProyecto : crea

    PagoController --> PagoService : usa
    PagoService --> PagoFactory : usa
```

> **Relación con Núcleo:** `Proyecto` contiene `0..*` `PagoProyecto`. El servicio delega la creación a la factory correspondiente según `TipoPago`.

---

## Módulo 5 — Compras, Proveedores y Materiales

Maneja las compras de insumos, su detalle por material y el catálogo de proveedores.

```mermaid
classDiagram
    class CompraProyecto {
        +id: String
        +fechaCompra: Date
        +numeroFactura: String
        +subtotal: Decimal
        +impuesto: Decimal
        +total: Decimal
        +observaciones: String
    }

    class DetalleCompra {
        +id: String
        +cantidad: Decimal
        +precioUnitario: Decimal
        +subtotal: Decimal
    }

    class Material {
        +id: String
        +codigoMaterial: String
        +nombre: String
        +unidadMedida: String
        +precioReferencia: Decimal
        +estado: String
    }

    class Proveedor {
        +id: String
        +nit: String
        +nombre: String
        +telefono: String
        +correo: String
        +contactoPrincipal: String
        +estado: String
    }

    class CompraController {
        +registrarCompraProyecto()
        +consultarComprasProyecto()
    }

    class CompraService {
        +registrarCompraProyecto()
        +agregarDetalleCompra()
        +calcularTotalCompra()
    }

    class IProveedorRepository {
        <<interface>>
        +save(proveedor)
        +findById(id)
        +findAll()
    }

    class ProveedorRepositoryMongo {
        +save(proveedor)
        +findById(id)
        +findAll()
    }

    class IMaterialRepository {
        <<interface>>
        +save(material)
        +findById(id)
        +findAll()
    }

    class MaterialRepositoryMongo {
        +save(material)
        +findById(id)
        +findAll()
    }

    CompraProyecto "1" *-- "1..*" DetalleCompra : contiene
    DetalleCompra "1" --> "1" Material : referencia
    CompraProyecto "1" --> "1" Proveedor : referencia

    CompraController --> CompraService : usa
    CompraService --> IProveedorRepository : usa
    CompraService --> IMaterialRepository : usa
    ProveedorRepositoryMongo ..|> IProveedorRepository : implementa
    MaterialRepositoryMongo ..|> IMaterialRepository : implementa
```

> **Relación con Núcleo:** `Proyecto` registra `0..*` `CompraProyecto`.

---

## Módulo 6 — Seguimiento y Documentos

Bitácora operativa: cada `SeguimientoProyecto` puede llevar evidencias adjuntas, y el proyecto almacena documentos generales.

```mermaid
classDiagram
    class SeguimientoProyecto {
        +id: String
        +fechaRegistro: Date
        +porcentajeAvance: Decimal
        +observaciones: String
    }

    class EvidenciaProyecto {
        +id: String
        +nombreArchivo: String
        +tipoArchivo: String
        +rutaArchivo: String
    }

    class DocumentoProyecto {
        +id: String
        +nombreArchivo: String
        +tipoArchivo: String
        +rutaArchivo: String
    }

    SeguimientoProyecto "1" *-- "0..*" EvidenciaProyecto : adjunta
```

> **Relaciones con Núcleo:**
> - `Proyecto` registra `0..*` `SeguimientoProyecto`.
> - `Proyecto` almacena `0..*` `DocumentoProyecto`.

---

## Módulo 7 — Patrones de Diseño (Observer + Strategy)

Patrones transversales que desacoplan al `Proyecto` de sus reacciones a eventos y de la lógica de cálculo de avance.

### 7.1 Observer — Notificación de eventos del proyecto

```mermaid
classDiagram
    class ProyectoEventPublisher {
        +attach(observer)
        +detach(observer)
        +notify(evento)
    }

    class IProyectoObserver {
        <<interface>>
        +update(evento)
    }

    class BitacoraProyectoObserver {
        +update(evento)
    }

    class IndicadoresProyectoObserver {
        +update(evento)
    }

    class AlertaPagosObserver {
        +update(evento)
    }

    ProyectoEventPublisher o--> "0..*" IProyectoObserver : notifica
    BitacoraProyectoObserver ..|> IProyectoObserver
    IndicadoresProyectoObserver ..|> IProyectoObserver
    AlertaPagosObserver ..|> IProyectoObserver
```

### 7.2 Strategy — Cálculo de avance

```mermaid
classDiagram
    class IAvanceProyectoStrategy {
        <<interface>>
        +calcularAvance(proyecto)
    }

    class AvancePorSeguimientosStrategy {
        +calcularAvance(proyecto)
    }

    class AvancePorFasesStrategy {
        +calcularAvance(proyecto)
    }

    AvancePorSeguimientosStrategy ..|> IAvanceProyectoStrategy
    AvancePorFasesStrategy ..|> IAvanceProyectoStrategy
```

> **Relación con Núcleo:**
> - `ProyectoService` publica eventos a través de `ProyectoEventPublisher`.
> - `ProyectoService.recalcularAvance()` delega en una `IAvanceProyectoStrategy` configurable.

---

## Módulo 8 — Infraestructura

Conexión única a MongoDB compartida por todos los repositorios. Aplica el **patrón Singleton**.

```mermaid
classDiagram
    class MongoConnection {
        <<singleton>>
        -instance: MongoConnection
        -client
        -database
        +getInstance()
        +getDatabase()
    }

    class IClienteRepository {
        <<interface>>
    }
    class IProyectoRepository {
        <<interface>>
    }
    class IContratistaRepository {
        <<interface>>
    }
    class IProveedorRepository {
        <<interface>>
    }
    class IMaterialRepository {
        <<interface>>
    }

    IClienteRepository ..> MongoConnection : obtiene conexión
    IProyectoRepository ..> MongoConnection : obtiene conexión
    IContratistaRepository ..> MongoConnection : obtiene conexión
    IProveedorRepository ..> MongoConnection : obtiene conexión
    IMaterialRepository ..> MongoConnection : obtiene conexión
```

---

## Mapa general de dependencias entre módulos

Vista de alto nivel para entender cómo se conectan los módulos sin entrar en clases individuales.

```mermaid
flowchart TB
    M2[Módulo 2<br/>Clientes]
    M1[Módulo 1<br/>Núcleo Proyecto]
    M3[Módulo 3<br/>Contratistas]
    M4[Módulo 4<br/>Pagos Cliente]
    M5[Módulo 5<br/>Compras]
    M6[Módulo 6<br/>Seguimiento y Documentos]
    M7[Módulo 7<br/>Patrones Observer + Strategy]
    M8[Módulo 8<br/>Infraestructura Mongo]

    M1 -->|referencia| M2
    M1 -->|contiene| M3
    M1 -->|contiene| M4
    M1 -->|registra| M5
    M1 -->|registra| M6
    M1 -.->|usa patrones| M7
    M2 -->|persiste en| M8
    M1 -->|persiste en| M8
    M3 -->|persiste en| M8
    M5 -->|persiste en| M8
```

---

## Notas de lectura

- **Cardinalidades:** se conservan las del diagrama original (`1`, `1..*`, `0..*`).
- **Estereotipos:** `<<interface>>`, `<<abstract>>`, `<<singleton>>`, `<<enumeration>>`.
- **Tipos de relación:**
  - `*--` composición fuerte (el contenedor controla el ciclo de vida).
  - `o--` agregación (referencia sin propiedad del ciclo de vida).
  - `-->` asociación / uso.
  - `..>` dependencia.
  - `..|>` realización de interfaz.
  - `<|--` herencia.
