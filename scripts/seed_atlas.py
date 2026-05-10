"""Seed MongoDB Atlas with sample Nigerian political posts."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from pymongo import MongoClient
from config import config
from dashboard.utils.mock_data import SAMPLE_POSTS

client = MongoClient(config.MONGODB_CONNECTION_STRING)
db = client[config.MONGODB_DATABASE_NAME]
collection = db["interpreted_posts"]

existing = collection.count_documents({})
if existing > 0:
    print(f"Database already has {existing} posts. Dropping old data...")
    collection.delete_many({})

posts = []
for p in SAMPLE_POSTS:
    posts.append({
        "source": p.get("source", "Unknown"),
        "location": p.get("location", "Unknown"),
        "content": p.get("content", ""),
        "topic": p.get("topic", "General"),
        "language_mix": ["English", "Pidgin"],
        "polarity": p.get("polarity", "Neutral"),
        "emotional_tone": p.get("emotional_tone", "Mixed"),
        "target_of_sentiment": p.get("target_of_sentiment", "General"),
        "sarcasm_detected": p.get("sarcasm_detected", False),
        "bot_or_campaign_risk": "Low",
        "confidence_score": p.get("confidence_score", 0.8),
        "explanation": p.get("explanation", ""),
        "interpreted_at": datetime.utcnow(),
    })

result = collection.insert_many(posts)
print(f"OK - Inserted {len(result.inserted_ids)} posts into MongoDB Atlas")
print(f"   Database: {config.MONGODB_DATABASE_NAME}")
print(f"   Collection: interpreted_posts")

client.close()
