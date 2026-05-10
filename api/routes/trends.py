# api/routes/trends.py
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from collections import Counter
from loguru import logger
from database.mongodb_client import mongodb_client

router = APIRouter()


@router.get("/")
async def get_trends(
    hours: int = Query(default=24, le=168)
):
    """Get sentiment trends over time"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=500
        )

        if not posts:
            return {
                "status": "success",
                "message": "No trend data available yet",
                "data": []
            }

        # Group by hour
        hourly_data = {}
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        for post in posts:
            interpreted_at = post.get("interpreted_at")
            if not interpreted_at:
                continue

            if isinstance(interpreted_at, str):
                try:
                    interpreted_at = datetime.fromisoformat(
                        interpreted_at
                    )
                except Exception:
                    continue

            if interpreted_at < cutoff:
                continue

            hour_key = interpreted_at.strftime(
                "%Y-%m-%d %H:00"
            )
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    "timestamp": hour_key,
                    "total": 0,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "dominant_emotion": "Mixed"
                }

            hourly_data[hour_key]["total"] += 1
            pol = post.get("polarity", "Neutral")
            if pol == "Positive":
                hourly_data[hour_key]["positive"] += 1
            elif pol == "Negative":
                hourly_data[hour_key]["negative"] += 1
            else:
                hourly_data[hour_key]["neutral"] += 1

        # Sort by timestamp
        trend_data = sorted(
            hourly_data.values(),
            key=lambda x: x["timestamp"]
        )

        return {
            "status": "success",
            "hours_analyzed": hours,
            "data_points": len(trend_data),
            "data": trend_data
        }

    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/hashtags")
async def get_trending_hashtags(
    limit: int = Query(default=10, le=50)
):
    """Get trending political hashtags"""
    try:
        raw_posts = mongodb_client.get_recent_posts(
            limit=500
        )

        all_hashtags = []
        for post in raw_posts:
            hashtags = post.get("hashtags", [])
            all_hashtags.extend(hashtags)

        hashtag_counts = Counter(all_hashtags)
        trending = [
            {"hashtag": tag, "count": count}
            for tag, count in
            hashtag_counts.most_common(limit)
            if tag
        ]

        return {
            "status": "success",
            "count": len(trending),
            "data": trending
        }

    except Exception as e:
        logger.error(
            f"Failed to get trending hashtags: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )