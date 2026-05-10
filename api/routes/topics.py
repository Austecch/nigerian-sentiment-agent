# api/routes/topics.py
from fastapi import APIRouter, Query, HTTPException
from collections import Counter
from loguru import logger
from database.mongodb_client import mongodb_client

router = APIRouter()


@router.get("/")
async def get_all_topics(
    limit: int = Query(default=10, le=50)
):
    """Get all tracked political topics"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=500
        )

        topic_counter = Counter(
            p.get("topic", "General") for p in posts
        )

        topics = []
        for topic, count in topic_counter.most_common(limit):
            topic_posts = [
                p for p in posts
                if p.get("topic") == topic
            ]
            positive = sum(
                1 for p in topic_posts
                if p.get("polarity") == "Positive"
            )
            negative = sum(
                1 for p in topic_posts
                if p.get("polarity") == "Negative"
            )

            topics.append({
                "topic": topic,
                "mention_count": count,
                "positive_percent": round(
                    positive / count * 100, 1
                ) if count > 0 else 0,
                "negative_percent": round(
                    negative / count * 100, 1
                ) if count > 0 else 0,
            })

        return {
            "status": "success",
            "count": len(topics),
            "data": topics
        }

    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{topic_name}")
async def get_topic_detail(
    topic_name: str,
    limit: int = Query(default=50, le=200)
):
    """Get detailed sentiment for a specific topic"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            topic=topic_name,
            limit=limit
        )

        if not posts:
            return {
                "status": "success",
                "message": f"No data for topic: {topic_name}",
                "data": {}
            }

        total = len(posts)
        emotions = Counter(
            p.get("emotional_tone", "Mixed")
            for p in posts
        )

        for post in posts:
            if "_id" in post:
                post["_id"] = str(post["_id"])

        return {
            "status": "success",
            "topic": topic_name,
            "total_mentions": total,
            "dominant_emotion": emotions.most_common(1)[0][0]
            if emotions else "Mixed",
            "posts": posts[:10]
        }

    except Exception as e:
        logger.error(f"Failed to get topic detail: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )