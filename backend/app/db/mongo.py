# app/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class Mongo:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongo = Mongo()

async def connect_to_mongo():
    mongo.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        tls=True,
    )
    mongo.db = mongo.client[settings.MONGO_DB_NAME]

async def close_mongo_connection():
    if mongo.client:
        mongo.client.close()


def get_collection(name: str):
    if mongo.db is None:
        raise RuntimeError("Database not initialized")
    return mongo.db[name]