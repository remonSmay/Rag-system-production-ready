import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from helpers.config import get_settings

logger = logging.getLogger("uvicorn.error")

_mongo_client: AsyncIOMotorClient | None = None
_db_client: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() :

    settings = get_settings()
    global _mongo_client, _db_client

    _mongo_client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        uuidRepresentation="standard",
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
    )

    # If Mongo is starting (e.g., docker compose just ran), give it a moment.
    for attempt in range(1, 11):
        try:
            await _mongo_client.admin.command("ping")
            break
        except Exception as exc:
            if attempt == 10:
                logger.error(
                    "MongoDB connection failed after retries (url=%s): %s",
                    settings.MONGODB_URL,
                    exc,
                )
                raise
            await asyncio.sleep(0.5)

    _db_client = _mongo_client[str(settings.MONGODB_DATABASE)]


def close_mongo_connection() -> None:
    global _mongo_client, _db_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _db_client = None


def get_db() -> AsyncIOMotorDatabase:
    if _db_client is None:
        raise RuntimeError("MongoDB client not initialized")
    return _db_client
