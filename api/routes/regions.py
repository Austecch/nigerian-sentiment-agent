# api/routes/regions.py
from fastapi import APIRouter, HTTPException
from collections import Counter
from loguru import logger
from database.mongodb_client import mongodb_client
from database.models import NIGERIAN_CITY_COORDINATES

router = APIRouter()


@router.get("/hotspots")
async def get_regional_hotspots():
    """
    Get geographic hotspot data for Nigeria map
    """
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=500
        )

        location_data = {}

        for post in posts:
            location = post.get("location", "Unknown")
            if location == "Unknown":
                continue

            if location not in location_data:
                location_data[location] = {
                    "mention_count": 0,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "emotions": [],
                }

            location_data[location]["mention_count"] += 1

            pol = post.get("polarity", "Neutral")
            if pol == "Positive":
                location_data[location]["positive"] += 1
            elif pol == "Negative":
                location_data[location]["negative"] += 1
            else:
                location_data[location]["neutral"] += 1

            emo = post.get("emotional_tone", "Mixed")
            location_data[location]["emotions"].append(emo)

        # Build response with coordinates
        hotspots = []
        for location, data in location_data.items():
            coords = NIGERIAN_CITY_COORDINATES.get(
                location, {}
            )

            emotion_counter = Counter(data["emotions"])
            dominant_emotion = (
                emotion_counter.most_common(1)[0][0]
                if emotion_counter else "Mixed"
            )

            count = data["mention_count"]
            dominant_sentiment = "Neutral"
            if data["positive"] > data["negative"]:
                dominant_sentiment = "Positive"
            elif data["negative"] > data["positive"]:
                dominant_sentiment = "Negative"

            hotspots.append({
                "location": location,
                "mention_count": count,
                "dominant_sentiment": dominant_sentiment,
                "dominant_emotion": dominant_emotion,
                "positive_percent": round(
                    data["positive"] / count * 100, 1
                ) if count > 0 else 0,
                "negative_percent": round(
                    data["negative"] / count * 100, 1
                ) if count > 0 else 0,
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
            })

        # Sort by mention count
        hotspots.sort(
            key=lambda x: x["mention_count"],
            reverse=True
        )

        return {
            "status": "success",
            "count": len(hotspots),
            "data": hotspots
        }

    except Exception as e:
        logger.error(f"Failed to get hotspots: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{location_name}")
async def get_location_sentiment(
    location_name: str
):
    """Get sentiment data for a specific location"""
    try:
        posts = mongodb_client.get_sentiment_summary(
            limit=500
        )

        location_posts = [
            p for p in posts
            if p.get("location", "").lower() ==
            location_name.lower()
        ]

        if not location_posts:
            return {
                "status": "success",
                "message": (
                    f"No data for location: {location_name}"
                ),
                "data": {}
            }

        total = len(location_posts)
        polarity = Counter(
            p.get("polarity", "Neutral")
            for p in location_posts
        )
        emotions = Counter(
            p.get("emotional_tone", "Mixed")
            for p in location_posts
        )
        topics = Counter(
            p.get("topic", "General")
            for p in location_posts
        )

        for post in location_posts:
            if "_id" in post:
                post["_id"] = str(post["_id"])

        return {
            "status": "success",
            "location": location_name,
            "total_mentions": total,
            "polarity_distribution": dict(polarity),
            "emotion_distribution": dict(emotions),
            "top_topics": dict(topics.most_common(5)),
            "recent_posts": location_posts[:5]
        }

    except Exception as e:
        logger.error(
            f"Failed to get location sentiment: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )