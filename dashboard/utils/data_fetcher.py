import requests
from loguru import logger
from dashboard.utils.mock_data import (
    SAMPLE_POSTS, TREND_DATA, HOTSPOT_DATA,
    TOPICS_DATA, SOURCE_DATA, SENTIMENTS, EMOTIONS
)

API_BASE_URL = "http://127.0.0.1:8000"


class DataFetcher:
    def __init__(self):
        self.base_url = API_BASE_URL

    def _try_api(self, method, endpoint, **kwargs):
        try:
            r = requests.request(method, f"{self.base_url}{endpoint}", timeout=10, **kwargs)
            if r.ok:
                return r.json()
        except Exception:
            pass
        return None

    def _mock_summary(self):
        total = len(SAMPLE_POSTS)
        return {
            "total_posts": total,
            "polarity": {
                "Positive": SENTIMENTS["Positive"],
                "Negative": SENTIMENTS["Negative"],
                "Neutral": SENTIMENTS["Neutral"],
                "positive_percent": round(SENTIMENTS["Positive"] / total * 100, 1),
                "negative_percent": round(SENTIMENTS["Negative"] / total * 100, 1),
                "neutral_percent": round(SENTIMENTS["Neutral"] / total * 100, 1),
            },
            "emotions": EMOTIONS,
        }

    def get_sentiment_summary(self, topic=None, limit=100) -> dict:
        result = self._try_api("GET", "/api/sentiment/summary", params={"limit": limit})
        if result and result.get("total_posts", 0) > 0:
            return result
        return self._mock_summary()

    def get_recent_posts(self, limit=50, source=None, polarity=None) -> dict:
        result = self._try_api("GET", "/api/sentiment/recent", params={"limit": limit})
        if result and result.get("count", 0) > 0:
            return result
        posts = SAMPLE_POSTS
        if source:
            posts = [p for p in posts if p.get("source") == source]
        if polarity:
            posts = [p for p in posts if p.get("polarity") == polarity]
        return {"status": "success", "count": len(posts), "data": posts[:limit]}

    def get_regional_hotspots(self) -> dict:
        result = self._try_api("GET", "/api/regions/hotspots")
        if result and result.get("data"):
            return result
        return {"status": "success", "data": HOTSPOT_DATA}

    def get_topics(self) -> dict:
        result = self._try_api("GET", "/api/topics/")
        if result and result.get("data"):
            return result
        return {"status": "success", "data": TOPICS_DATA}

    def get_trends(self, hours: int = 24) -> dict:
        result = self._try_api("GET", "/api/trends/", params={"hours": hours})
        if result and result.get("data"):
            return result
        return {"status": "success", "data": TREND_DATA}

    def get_trending_hashtags(self, limit=10) -> dict:
        result = self._try_api("GET", "/api/trends/hashtags", params={"limit": limit})
        if result and result.get("data"):
            return result
        return {"status": "success", "data": [
            {"hashtag": "#NigeriaDecides", "count": 1250},
            {"hashtag": "#Sapa", "count": 980},
            {"hashtag": "#RenewedHope", "count": 740},
            {"hashtag": "#Obidient", "count": 620},
            {"hashtag": "#FuelSubsidy", "count": 510},
        ]}

    def trigger_pipeline(self, max_posts=50) -> dict:
        result = self._try_api("POST", "/api/pipeline/run", params={"max_posts": max_posts})
        return result if result else {"status": "success", "message": "Mock pipeline completed"}

    def check_api_health(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/api/health", timeout=3).status_code == 200
        except Exception:
            return False


data_fetcher = DataFetcher()
