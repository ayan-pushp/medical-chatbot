
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import AsyncGenerator
from contextlib import asynccontextmanager

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.get_database("docbot")
    # Create indexes
    try:
        await client.admin.command('ping')
        await db.users.create_index("username", unique=True)
        await db.chats.create_index([("user_id", 1), ("timestamp", -1)])
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise
    
@asynccontextmanager
async def get_db():
    if db is None:
        await init_db()
    yield db