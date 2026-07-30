"""MongoDB database connection and collections."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongo():
    """Create database connection on startup."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db.db = db.client[settings.MONGODB_DB_NAME]

    # Create indexes
    await db.db.users.create_index("email", unique=True)
    await db.db.users.create_index("username", unique=True)
    await db.db.predictions.create_index("user_id")
    await db.db.predictions.create_index("created_at")
    await db.db.skills.create_index([("user_id", 1), ("skill_name", 1)], unique=True)
    await db.db.projects.create_index("user_id")
    await db.db.roadmaps.create_index("user_id")

    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close database connection on shutdown."""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    return db.db