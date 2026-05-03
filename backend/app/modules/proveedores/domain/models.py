from pydantic import BaseModel, EmailStr, Field

from app.shared.catalogs import EstadoRegistro


class ProveedorBase(BaseModel):
    nit: str = Field(min_length=5)
    nombre: str = Field(min_length=3)
    telefono: str = Field(min_length=7)
    correo: EmailStr
    direccion: str = Field(min_length=5)
    contactoPrincipal: str = Field(min_length=3)
    estado: EstadoRegistro = EstadoRegistro.ACTIVO
    observaciones: str = ""


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(ProveedorBase):
    pass


class ProveedorResponse(ProveedorBase):
    id: str
    createdAt: str
    updatedAt: str