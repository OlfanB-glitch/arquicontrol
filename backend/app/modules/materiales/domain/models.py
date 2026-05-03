from pydantic import BaseModel, Field

from app.shared.catalogs import EstadoRegistro


class MaterialBase(BaseModel):
    codigoMaterial: str = Field(min_length=3)
    nombre: str = Field(min_length=3)
    unidadMedida: str = Field(min_length=1)
    descripcion: str = ""
    precioReferencia: float = Field(ge=0)
    estado: EstadoRegistro = EstadoRegistro.ACTIVO


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: str
    createdAt: str
    updatedAt: str