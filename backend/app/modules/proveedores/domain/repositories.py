from abc import ABC, abstractmethod


class IProveedorRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, proveedor_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_nit(self, nit: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, proveedor_data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def update(self, proveedor_id: str, proveedor_data: dict) -> dict | None:
        raise NotImplementedError