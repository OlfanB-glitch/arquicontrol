from abc import ABC, abstractmethod


class IMaterialRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, material_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(self, code: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, material_data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def update(self, material_id: str, material_data: dict) -> dict | None:
        raise NotImplementedError