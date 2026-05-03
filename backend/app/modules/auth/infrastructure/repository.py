from app.core.database import get_database


class AuthRepository:
    def __init__(self):
        self.collection = get_database().usuarios

    async def get_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({"email": email}, {"_id": 0})

    async def get_by_id(self, user_id: str) -> dict | None:
        return await self.collection.find_one({"id": user_id}, {"_id": 0})

    async def count(self) -> int:
        return await self.collection.count_documents({})

    async def insert_one(self, user_data: dict):
        await self.collection.insert_one(dict(user_data))