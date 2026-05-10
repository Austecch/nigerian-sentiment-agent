# database/mongodb_client.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from loguru import logger
from config import config


class MongoDBClient:
    """Handles all MongoDB database operations"""

    def __init__(self):
        self.connection_string = config.MONGODB_CONNECTION_STRING
        self.database_name = config.MONGODB_DATABASE_NAME
        self.async_client = None
        self.sync_client = None
        self.db = None

    def connect_sync(self):
        """Synchronous connection for simple operations"""
        try:
            self.sync_client = MongoClient(self.connection_string)
            self.db = self.sync_client[self.database_name]
            logger.info(f"Connected to MongoDB: {self.database_name}")
            return self.db
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    async def connect_async(self):
        """Asynchronous connection for API operations"""
        try:
            self.async_client = AsyncIOMotorClient(
                self.connection_string
            )
            self.db = self.async_client[self.database_name]
            logger.info(
                f"Async connected to MongoDB: {self.database_name}"
            )
            return self.db
        except Exception as e:
            logger.error(f"MongoDB async connection failed: {e}")
            raise

    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if self.db is None:
            self.connect_sync()
        return self.db[collection_name]

    def save_raw_post(self, post_data: dict) -> str:
        """Save a raw scraped post to database"""
        try:
            collection = self.get_collection("raw_posts")
            result = collection.insert_one(post_data)
            logger.info(f"Saved raw post: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save raw post: {e}")
            raise

    def save_interpreted_post(self, post_data: dict) -> str:
        """Save an interpreted post to database"""
        try:
            collection = self.get_collection("interpreted_posts")
            result = collection.insert_one(post_data)
            logger.info(
                f"Saved interpreted post: {result.inserted_id}"
            )
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save interpreted post: {e}")
            raise

    def save_many_raw_posts(self, posts: list) -> int:
        """Save multiple raw posts at once"""
        try:
            if not posts:
                return 0
            collection = self.get_collection("raw_posts")
            result = collection.insert_many(posts)
            count = len(result.inserted_ids)
            logger.info(f"Saved {count} raw posts")
            return count
        except Exception as e:
            logger.error(f"Failed to save multiple posts: {e}")
            raise

    def get_recent_posts(
        self,
        limit: int = 100,
        source: str = None
    ) -> list:
        """Get recent posts from database"""
        try:
            collection = self.get_collection("raw_posts")
            query = {}
            if source:
                query["source"] = source
            posts = list(
                collection.find(query)
                .sort("scraped_at", -1)
                .limit(limit)
            )
            return posts
        except Exception as e:
            logger.error(f"Failed to get recent posts: {e}")
            return []

    def get_sentiment_summary(
        self,
        topic: str = None,
        limit: int = 50
    ) -> list:
        """Get sentiment summaries for dashboard"""
        try:
            collection = self.get_collection(
                "interpreted_posts"
            )
            query = {}
            if topic:
                query["topic"] = topic
            posts = list(
                collection.find(query)
                .sort("interpreted_at", -1)
                .limit(limit)
            )
            return posts
        except Exception as e:
            logger.error(f"Failed to get sentiment summary: {e}")
            return []

    def check_duplicate(self, content: str) -> bool:
        """Check if a post already exists in database"""
        try:
            collection = self.get_collection("raw_posts")
            existing = collection.find_one({"content": content})
            return existing is not None
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}")
            return False

    def close(self):
        """Close database connections"""
        if self.sync_client:
            self.sync_client.close()
        if self.async_client:
            self.async_client.close()
        logger.info("MongoDB connections closed")


# Single instance to use across project
mongodb_client = MongoDBClient()
