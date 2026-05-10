# database/queries.py
"""
Database query helpers for common operations.
Provides optimized query methods for sentiment analysis.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
from .mongodb_client import mongodb_client


def get_posts_by_date_range(
    start_date: datetime,
    end_date: datetime,
    source: Optional[str] = None,
    limit: int = 1000
) -> List[Dict]:
    """
    Get posts within a date range.
    
    Args:
        start_date: Start of date range
        end_date: End of date range
        source: Optional filter by source
        limit: Maximum number of posts to return
    
    Returns:
        List of post dictionaries
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        query = {
            "interpreted_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        if source:
            query["source"] = source
        
        posts = list(
            collection.find(query)
            .sort("interpreted_at", -1)
            .limit(limit)
        )
        return posts
    except Exception as e:
        logger.error(f"Failed to get posts by date range: {e}")
        return []


def get_posts_by_location(
    location: str,
    limit: int = 100
) -> List[Dict]:
    """
    Get posts from a specific location.
    
    Args:
        location: Location name (e.g., "Lagos")
        limit: Maximum number of posts to return
    
    Returns:
        List of post dictionaries
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        posts = list(
            collection.find({"location": location})
            .sort("interpreted_at", -1)
            .limit(limit)
        )
        return posts
    except Exception as e:
        logger.error(f"Failed to get posts by location: {e}")
        return []


def get_sentiment_by_topic(
    topic: str,
    days: int = 7
) -> Dict:
    """
    Get sentiment distribution for a topic over the last N days.
    
    Args:
        topic: Topic to analyze
        days: Number of days to look back
    
    Returns:
        Dictionary with sentiment counts and percentages
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        start_date = datetime.utcnow() - timedelta(days=days)
        
        posts = list(
            collection.find({
                "topic": topic,
                "interpreted_at": {"$gte": start_date}
            })
        )
        
        polarity_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for post in posts:
            pol = post.get("polarity", "Neutral")
            if pol in polarity_counts:
                polarity_counts[pol] += 1
        
        total = len(posts)
        if total > 0:
            return {
                "topic": topic,
                "total": total,
                "positive": polarity_counts["Positive"],
                "negative": polarity_counts["Negative"],
                "neutral": polarity_counts["Neutral"],
                "positive_percent": round(polarity_counts["Positive"] / total * 100, 1),
                "negative_percent": round(polarity_counts["Negative"] / total * 100, 1),
                "neutral_percent": round(polarity_counts["Neutral"] / total * 100, 1),
            }
        return {"topic": topic, "total": 0}
    except Exception as e:
        logger.error(f"Failed to get sentiment by topic: {e}")
        return {}


def get_trend_data(
    hours: int = 24,
    interval: str = "hour"  # hour, day, week
) -> List[Dict]:
    """
    Get sentiment trend data over time.
    
    Args:
        hours: Number of hours to look back
        interval: Grouping interval (hour, day, week)
    
    Returns:
        List of dictionaries with timestamp and counts
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        posts = list(
            collection.find({
                "interpreted_at": {"$gte": start_time}
            })
        )
        
        # Group by interval
        trend_data = {}
        for post in posts:
            interpreted_at = post.get("interpreted_at")
            if not interpreted_at:
                continue
            
            if interval == "hour":
                key = interpreted_at.strftime("%Y-%m-%d %H:00")
            elif interval == "day":
                key = interpreted_at.strftime("%Y-%m-%d")
            else:  # week
                # Get the Monday of that week
                monday = interpreted_at - timedelta(days=interpreted_at.weekday())
                key = monday.strftime("%Y-%m-%d")
            
            if key not in trend_data:
                trend_data[key] = {
                    "timestamp": key,
                    "total": 0,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                }
            
            trend_data[key]["total"] += 1
            pol = post.get("polarity", "Neutral")
            if pol == "Positive":
                trend_data[key]["positive"] += 1
            elif pol == "Negative":
                trend_data[key]["negative"] += 1
            else:
                trend_data[key]["neutral"] += 1
        
        # Convert to list and sort by timestamp
        result = list(trend_data.values())
        result.sort(key=lambda x: x["timestamp"])
        return result
    except Exception as e:
        logger.error(f"Failed to get trend data: {e}")
        return []


def get_geographic_summary() -> Dict:
    """
    Get summary of sentiment by geographic location.
    
    Returns:
        Dictionary with location data
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        pipeline = [
            {
                "$group": {
                    "_id": "$location",
                    "total": {"$sum": 1},
                    "positive": {
                        "$sum": {
                            "$cond": [{"$eq": ["$polarity", "Positive"]}, 1, 0]
                        }
                    },
                    "negative": {
                        "$sum": {
                            "$cond": [{"$eq": ["$polarity", "Negative"]}, 1, 0]
                        }
                    },
                    "neutral": {
                        "$sum": {
                            "$cond": [{"$eq": ["$polarity", "Neutral"]}, 1, 0]
                        }
                    }
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": 20}
        ]
        
        results = list(collection.aggregate(pipeline))
        return {r["_id"]: r for r in results if r["_id"] != "Unknown"}
    except Exception as e:
        logger.error(f"Failed to get geographic summary: {e}")
        return {}


def get_hotspots(limit: int = 10) -> List[Dict]:
    """
    Get top locations with sentiment data.
    
    Args:
        limit: Maximum number of hotspots to return
    
    Returns:
        List of hotspot dictionaries with location and sentiment data
    """
    try:
        collection = mongodb_client.get_collection("interpreted_posts")
        pipeline = [
            {
                "$group": {
                    "_id": "$location",
                    "mention_count": {"$sum": 1},
                    "positive": {
                        "$sum": {
                            "$cond": [{"$eq": ["$polarity", "Positive"]}, 1, 0]
                        }
                    },
                    "negative": {
                        "$sum": {
                            "$cond": [{"$eq": ["$polarity", "Negative"]}, 1, 0]
                        }
                    }
                }
            },
            {"$sort": {"mention_count": -1}},
            {"$limit": limit}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Add coordinates from models
        from .models import NIGERIAN_CITY_COORDINATES
        
        hotspots = []
        for r in results:
            location = r["_id"]
            if location == "Unknown":
                continue
            
            coords = NIGERIAN_CITY_COORDINATES.get(location, {})
            hotspot = {
                "location": location,
                "mention_count": r["mention_count"],
                "positive": r.get("positive", 0),
                "negative": r.get("negative", 0),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
            }
            hotspots.append(hotspot)
        
        return hotspots
    except Exception as e:
        logger.error(f"Failed to get hotspots: {e}")
        return []


def cleanup_old_data(days: int = 90):
    """
    Remove raw posts older than specified days.
    
    Args:
        days: Delete posts older than this
    
    Returns:
        Number of deleted posts
    """
    try:
        collection = mongodb_client.get_collection("raw_posts")
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = collection.delete_many({
            "scraped_at": {"$lt": cutoff}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old raw posts")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return 0
