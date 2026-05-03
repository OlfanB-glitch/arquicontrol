from abc import ABC, abstractmethod


class IClienteRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, client_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_document(self, document_number: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, client_data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def update(self, client_id: str, client_data: dict) -> dict | None:
        raise NotImplementedError