from pydantic import BaseModel, EmailStr, Field

from app.shared.catalogs import EstadoRegistro


class ClienteBase(BaseModel):
    tipoDocumento: str = Field(min_length=2)
    numeroDocumento: str = Field(min_length=4)
    nombreCompleto: str = Field(min_length=3)
    telefono: str = Field(min_length=7)
    correo: EmailStr
    direccion: str = Field(min_length=5)
    ciudad: str = Field(min_length=2)
    datosFacturacion: dict | None = None
    observaciones: str = ""
    fechaPrimerContacto: str
    estado: EstadoRegistro = EstadoRegistro.ACTIVO


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: str
    createdAt: str
    updatedAt: str