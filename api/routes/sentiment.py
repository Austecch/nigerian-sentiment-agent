# api/routes/sentiment.py
from fastapi import APIRouter, Query, HTTPException
from loguru import logger
from database.mongodb_client import mongodb_client

router = APIRouter()


@router.get("/recent")
async def get_recent_sentiment(
    limit: int = Query(default=50, le=200),
    source: str = Query(default=None),
    polarity: str = Query(default=None),
):
    """Get recent interpreted sentiment posts"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=limit
        )

        # Apply filters
        if source:
            posts = [
                p for p in posts
                if p.get("source") == source
            ]
        if polarity:
            posts = [
                p for p in posts
                if p.get("polarity") == polarity
            ]

        # Clean MongoDB ObjectId for JSON response
        for post in posts:
            if "_id" in post:
                post["_id"] = str(post["_id"])

        return {
            "status": "success",
            "count": len(posts),
            "data": posts
        }

    except Exception as e:
        logger.error(f"Failed to get recent sentiment: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/summary")
async def get_sentiment_summary(
    topic: str = Query(default=None),
    limit: int = Query(default=100, le=500),
):
    """Get aggregated sentiment summary"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            topic=topic,
            limit=limit
        )

        if not posts:
            return {
                "status": "success",
                "message": "No data available yet",
                "data": {}
            }

        # Calculate summary
        total = len(posts)
        polarity_counts = {
            "Positive": 0,
            "Negative": 0,
            "Neutral": 0
        }
        emotion_counts = {
            "Hope": 0,
            "Anger": 0,
            "Apathy": 0,
            "Excitement": 0,
            "Mixed": 0
        }

        for post in posts:
            pol = post.get("polarity", "Neutral")
            if pol in polarity_counts:
                polarity_counts[pol] += 1

            emo = post.get("emotional_tone", "Mixed")
            if emo in emotion_counts:
                emotion_counts[emo] += 1

        return {
            "status": "success",
            "total_posts": total,
            "polarity": {
                **polarity_counts,
                "positive_percent": round(
                    polarity_counts["Positive"]
                    / total * 100, 1
                ),
                "negative_percent": round(
                    polarity_counts["Negative"]
                    / total * 100, 1
                ),
                "neutral_percent": round(
                    polarity_counts["Neutral"]
                    / total * 100, 1
                ),
            },
            "emotions": emotion_counts,
        }

    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/by-source")
async def get_sentiment_by_source():
    """Get sentiment breakdown by source"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=500
        )

        sources = {}
        for post in posts:
            source = post.get("source", "Unknown")
            if source not in sources:
                sources[source] = {
                    "total": 0,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                }
            sources[source]["total"] += 1
            pol = post.get("polarity", "Neutral")
            if pol == "Positive":
                sources[source]["positive"] += 1
            elif pol == "Negative":
                sources[source]["negative"] += 1
            else:
                sources[source]["neutral"] += 1

        return {
            "status": "success",
            "data": sources
        }

    except Exception as e:
        logger.error(
            f"Failed to get sentiment by source: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )