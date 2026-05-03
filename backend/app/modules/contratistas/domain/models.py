from pydantic import BaseModel, EmailStr, Field

from app.shared.catalogs import EstadoRegistro


class ContratistaBase(BaseModel):
    tipoDocumento: str = Field(min_length=2)
    numeroDocumento: str = Field(min_length=4)
    nombreCompleto: str = Field(min_length=3)
    especialidad: str = Field(min_length=3)
    telefono: str = Field(min_length=7)
    correo: EmailStr
    direccion: str = Field(min_length=5)
    tarifaBase: float = Field(ge=0)
    estado: EstadoRegistro = EstadoRegistro.ACTIVO


class ContratistaCreate(ContratistaBase):
    pass


class ContratistaUpdate(ContratistaBase):
    pass


class ContratistaResponse(ContratistaBase):
    id: str
    createdAt: str
    updatedAt: str