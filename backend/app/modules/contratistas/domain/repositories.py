from abc import ABC, abstractmethod


class IContratistaRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, contractor_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_document(self, document_number: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, contractor_data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def update(self, contractor_id: str, contractor_data: dict) -> dict | None:
        raise NotImplementedError