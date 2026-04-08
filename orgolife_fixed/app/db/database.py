"""
MongoDB async connection using Motor.
Provides a singleton DB client injected across the app.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db_instance = Database()


async def connect_db() -> None:
    """Open MongoDB connection on application startup."""
    try:
        db_instance.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=10000,  # 10s — enough for Atlas cold-start
            connectTimeoutMS=10000,
            socketTimeoutMS=30000,
        )
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        # Verify connection
        await db_instance.client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise


async def close_db() -> None:
    """Close MongoDB connection on application shutdown."""
    if db_instance.client:
        db_instance.client.close()
        logger.info("🔌 MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance. Raises RuntimeError if not connected."""
    if db_instance.db is None:
        raise RuntimeError(
            "Database not initialised. Ensure connect_db() ran during app startup."
        )
    return db_instance.db


# ── Collection accessors ─────────────────────────────────────────

def get_users_collection():
    return db_instance.db["users"]

def get_donors_collection():
    return db_instance.db["donors"]

def get_receivers_collection():
    return db_instance.db["receivers"]

def get_hospitals_collection():
    return db_instance.db["hospitals"]

def get_organ_registrations_collection():
    return db_instance.db["organ_registrations"]
