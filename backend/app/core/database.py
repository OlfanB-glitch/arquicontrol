from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoConnection:
    """Singleton para mantener una única conexión activa a MongoDB."""

    _instance = None
    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = AsyncIOMotorClient(settings.mongo_url)
            cls._database = cls._client[settings.db_name]
        return cls._instance

    @property
    def client(self) -> AsyncIOMotorClient:
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        return self._database

    def close(self):
        if self._client is not None:
            self._client.close()


def get_database() -> AsyncIOMotorDatabase:
    return MongoConnection().database