from pydantic import BaseModel, Field, model_validator

from app.shared.catalogs import EstadoAsignacion, EstadoProyecto, TipoPago, TipoProyecto


class AreaInfo(BaseModel):
    valor: float = Field(ge=0)
    unidad: str = Field(min_length=1)
    tipoArea: str = Field(min_length=2)


class FaseCreate(BaseModel):
    nombre: str = Field(min_length=3)
    descripcion: str = ""
    porcentajePlaneado: float = Field(default=0, ge=0, le=100)
    porcentajeAvance: float = Field(default=0, ge=0, le=100)
    fechaInicio: str | None = None
    fechaFinEstimada: str | None = None
    estado: str = "PENDIENTE"


class FaseInfo(FaseCreate):
    id: str
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class FaseUpdate(FaseCreate):
    pass


class EvidenciaUrlCreate(BaseModel):
    nombre: str = Field(min_length=3)
    url: str = Field(min_length=5)
    descripcion: str = ""


class EvidenciaInfo(BaseModel):
    id: str
    tipo: str
    nombre: str
    url: str
    descripcion: str = ""
    fuente: str
    fechaRegistro: str
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class SeguimientoCreate(BaseModel):
    faseId: str
    fecha: str
    observaciones: str = Field(min_length=3)
    porcentajeAvance: float = Field(ge=0, le=100)
    evidencias: list[EvidenciaUrlCreate] = Field(default_factory=list)


class SeguimientoInfo(SeguimientoCreate):
    id: str
    evidencias: list[EvidenciaInfo] = Field(default_factory=list)
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class SeguimientoUpdate(SeguimientoCreate):
    pass


class PagoCreate(BaseModel):
    tipoPago: TipoPago
    faseId: str | None = None
    fechaPago: str
    monto: float = Field(ge=0)
    metodoPago: str = Field(min_length=3)
    referencia: str = ""
    concepto: str = Field(min_length=3)
    observaciones: str = ""

    @model_validator(mode="after")
    def validate_phase_rules(self):
        if self.tipoPago == TipoPago.PAGO_POR_FASE and not self.faseId:
            raise ValueError("faseId es obligatorio para pagos por fase")
        return self


class PagoInfo(PagoCreate):
    idPago: str
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class PagoUpdate(PagoCreate):
    pass


class AvanceContratistaCreate(BaseModel):
    fecha: str
    descripcion: str = Field(min_length=3)
    jornadaHoras: float = Field(default=0, ge=0)
    porcentajeAvance: float = Field(default=0, ge=0, le=100)


class AvanceContratistaInfo(AvanceContratistaCreate):
    id: str


class PagoContratistaCreate(BaseModel):
    fechaPago: str
    monto: float = Field(ge=0)
    referencia: str = ""
    observaciones: str = ""


class PagoContratistaInfo(PagoContratistaCreate):
    id: str


class AsignacionContratistaCreate(BaseModel):
    contratistaId: str
    rol: str = Field(min_length=3)
    fechaInicio: str
    fechaFin: str | None = None
    valorAcordado: float = Field(ge=0)
    estado: EstadoAsignacion = EstadoAsignacion.ACTIVA


class AsignacionContratistaInfo(AsignacionContratistaCreate):
    idAsignacion: str
    avances: list[AvanceContratistaInfo] = Field(default_factory=list)
    pagosContratista: list[PagoContratistaInfo] = Field(default_factory=list)
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class AsignacionContratistaUpdate(AsignacionContratistaCreate):
    pass


class DetalleCompraCreate(BaseModel):
    materialId: str
    cantidad: float = Field(gt=0)
    precioUnitario: float = Field(ge=0)


class DetalleCompraInfo(DetalleCompraCreate):
    idDetalle: str
    subtotal: float = Field(ge=0)


class CompraCreate(BaseModel):
    proveedorId: str
    fechaCompra: str
    numeroFactura: str = Field(min_length=3)
    impuesto: float = Field(default=0, ge=0)
    observaciones: str = ""
    detalleCompra: list[DetalleCompraCreate]

    @model_validator(mode="after")
    def validate_details(self):
        if not self.detalleCompra:
            raise ValueError("La compra debe tener al menos un detalle")
        return self


class CompraInfo(BaseModel):
    idCompra: str
    proveedorId: str
    fechaCompra: str
    numeroFactura: str
    subtotal: float = Field(ge=0)
    impuesto: float = Field(ge=0)
    total: float = Field(ge=0)
    observaciones: str = ""
    detalleCompra: list[DetalleCompraInfo] = Field(default_factory=list)
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class CompraUpdate(CompraCreate):
    pass


class DocumentoUrlCreate(BaseModel):
    nombre: str = Field(min_length=3)
    url: str = Field(min_length=5)
    tipo: str = Field(min_length=2)
    seguimientoId: str | None = None
    observaciones: str = ""


class DocumentoInfo(BaseModel):
    id: str
    nombre: str
    url: str
    tipo: str
    fuente: str
    seguimientoId: str | None = None
    observaciones: str = ""
    fechaRegistro: str
    isActive: bool = True
    deletedAt: str | None = None
    deletedBy: str | None = None
    motivo: str | None = None
    updatedAt: str | None = None


class DocumentoUpdate(BaseModel):
    nombre: str = Field(min_length=3)
    url: str = Field(min_length=1)
    tipo: str = Field(min_length=2)
    seguimientoId: str | None = None
    observaciones: str = ""


class DeleteEmbeddedRequest(BaseModel):
    motivo: str = Field(min_length=1, max_length=250)

    @model_validator(mode="after")
    def validate_motivo(self):
        self.motivo = self.motivo.strip()
        if not self.motivo:
            raise ValueError("El motivo es obligatorio para realizar la baja lógica")
        return self


class ResumenFinanciero(BaseModel):
    totalPagadoCliente: float = 0
    saldoPendienteCliente: float = 0
    totalCompras: float = 0
    totalPagadoContratistas: float = 0
    costoTotalEjecutado: float = 0
    margenEstimado: float = 0


class AlertaProyecto(BaseModel):
    id: str
    tipo: str
    nivel: str
    mensaje: str
    createdAt: str


class ProyectoBase(BaseModel):
    codigoProyecto: str = Field(min_length=3)
    clienteId: str
    nombreProyecto: str = Field(min_length=3)
    tipoProyecto: TipoProyecto
    descripcion: str = Field(min_length=5)
    ubicacion: str = Field(min_length=5)
    area: AreaInfo
    presupuestoEstimado: float = Field(ge=0)
    valorContrato: float = Field(ge=0)
    estadoProyecto: EstadoProyecto = EstadoProyecto.PENDIENTE
    fechaInicio: str
    fechaFinEstimada: str
    porcentajeAvanceGeneral: float = Field(default=0, ge=0, le=100)
    observacionesGenerales: str = ""
    metodoCalculoAvance: str = "SEGUIMIENTOS"


class ProyectoCreate(ProyectoBase):
    fases: list[FaseCreate] = Field(default_factory=list)


class ProyectoUpdate(ProyectoBase):
    fases: list[FaseCreate] = Field(default_factory=list)


class ProyectoResponse(ProyectoBase):
    id: str
    fases: list[FaseInfo] = Field(default_factory=list)
    seguimientos: list[SeguimientoInfo] = Field(default_factory=list)
    pagos: list[PagoInfo] = Field(default_factory=list)
    contratistasAsignados: list[AsignacionContratistaInfo] = Field(default_factory=list)
    compras: list[CompraInfo] = Field(default_factory=list)
    documentos: list[DocumentoInfo] = Field(default_factory=list)
    resumenFinanciero: ResumenFinanciero = Field(default_factory=ResumenFinanciero)
    bitacora: list[dict] = Field(default_factory=list)
    alertas: list[AlertaProyecto] = Field(default_factory=list)
    indicadores: dict = Field(default_factory=dict)
    createdAt: str
    updatedAt: str