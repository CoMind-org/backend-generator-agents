from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import require_mongo_settings, settings

require_mongo_settings()

client = AsyncIOMotorClient(settings.mongo_uri)

db = client[settings.database_name]
