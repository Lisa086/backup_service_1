from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    return db.client

async def connect_to_mongo():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@mongodb:27017")
    db.client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000
    )
    print("Подключение к MongoDB установлено")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Подключение к MongoDB закрыто")
