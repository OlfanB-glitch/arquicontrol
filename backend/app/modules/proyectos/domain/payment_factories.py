from abc import ABC, abstractmethod

from fastapi import HTTPException

from app.modules.proyectos.domain.models import PagoCreate
from app.shared.catalogs import TipoPago
from app.shared.common import generate_id


class PagoFactory(ABC):
    @abstractmethod
    def create(self, payload: PagoCreate) -> dict:
        raise NotImplementedError


class AnticipoFactory(PagoFactory):
    def create(self, payload: PagoCreate) -> dict:
        payment = payload.model_dump()
        payment["idPago"] = generate_id()
        payment["faseId"] = None
        return payment


class PagoPorFaseFactory(PagoFactory):
    def create(self, payload: PagoCreate) -> dict:
        if not payload.faseId:
            raise HTTPException(status_code=422, detail="faseId es obligatorio para pagos por fase")
        payment = payload.model_dump()
        payment["idPago"] = generate_id()
        return payment


class PagoGeneralFactory(PagoFactory):
    def create(self, payload: PagoCreate) -> dict:
        payment = payload.model_dump()
        payment["idPago"] = generate_id()
        payment["faseId"] = None
        return payment


class PagoFactoryResolver:
    def resolve(self, tipo_pago: TipoPago) -> PagoFactory:
        if tipo_pago == TipoPago.ANTICIPO:
            return AnticipoFactory()
        if tipo_pago == TipoPago.PAGO_POR_FASE:
            return PagoPorFaseFactory()
        return PagoGeneralFactory()