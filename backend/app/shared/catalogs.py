from enum import Enum


class TipoProyecto(str, Enum):
    VIVIENDA = "VIVIENDA"
    REMODELACION = "REMODELACION"
    AMPLIACION = "AMPLIACION"
    ADECUACION_INTERIOR = "ADECUACION_INTERIOR"
    DISENO_COMERCIAL = "DISENO_COMERCIAL"
    OTRO = "OTRO"


class EstadoProyecto(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_COTIZACION = "EN_COTIZACION"
    EN_DISENO = "EN_DISENO"
    EN_EJECUCION = "EN_EJECUCION"
    SUSPENDIDO = "SUSPENDIDO"
    FINALIZADO = "FINALIZADO"
    ENTREGADO = "ENTREGADO"


class TipoPago(str, Enum):
    ANTICIPO = "ANTICIPO"
    PAGO_POR_FASE = "PAGO_POR_FASE"
    PAGO_GENERAL = "PAGO_GENERAL"


class EstadoAsignacion(str, Enum):
    ACTIVA = "ACTIVA"
    SUSPENDIDA = "SUSPENDIDA"
    FINALIZADA = "FINALIZADA"


class EstadoRegistro(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


def enum_values(enum_class) -> list[str]:
    return [item.value for item in enum_class]