from abc import ABC, abstractmethod


class IProyectoRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, project_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(self, project_code: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, project_data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def replace(self, project_id: str, project_data: dict) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def aggregate_recent_payments(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def aggregate_recent_purchases(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def aggregate_documents(self) -> list[dict]:
        raise NotImplementedError