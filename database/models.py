# database/models.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RawPost(BaseModel):
    """Represents a raw scraped post before interpretation"""

    source: str
    # X, Nairaland, NewsComment
    url: Optional[str] = None
    content: str
    author: Optional[str] = None
    location: Optional[str] = "Unknown"
    hashtags: Optional[List[str]] = []
    timestamp: Optional[datetime] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    is_duplicate: bool = False
    bot_risk: str = "Low"
    # Low, Medium, High
    raw_id: Optional[str] = None


class InterpretedPost(BaseModel):
    """Represents a post after cultural interpretation"""

    raw_post_id: Optional[str] = None
    source: str
    location: str = "Unknown"
    content: str
    topic: Optional[str] = "General"
    language_mix: List[str] = ["English"]
    polarity: Optional[str] = "Neutral"
    # Positive, Negative, Neutral
    emotional_tone: Optional[str] = "Mixed"
    # Hope, Anger, Apathy, Excitement, Mixed
    target_of_sentiment: Optional[str] = "General"
    # Policy, Personality, Economy, Party, Governance, Security
    sarcasm_detected: bool = False
    bot_or_campaign_risk: str = "Low"
    confidence_score: float = 0.0
    explanation: Optional[str] = None
    interpreted_at: datetime = Field(default_factory=datetime.utcnow)


class SentimentSummary(BaseModel):
    """Aggregated sentiment for dashboard display"""

    topic: str
    time_period: str
    total_volume: int = 0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    dominant_emotion: str = "Mixed"
    hope_count: int = 0
    anger_count: int = 0
    apathy_count: int = 0
    excitement_count: int = 0
    mixed_count: int = 0
    top_locations: List[str] = []
    top_hashtags: List[str] = []
    sarcasm_rate: float = 0.0
    bot_risk_rate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LocationHotspot(BaseModel):
    """Geographic sentiment data for map visualization"""

    location: str
    latitude: float
    longitude: float
    mention_count: int = 0
    dominant_sentiment: str = "Neutral"
    dominant_emotion: str = "Mixed"
    top_topics: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Nigerian city coordinates for mapping
NIGERIAN_CITY_COORDINATES = {
    "Lagos": {"latitude": 6.5244, "longitude": 3.3792},
    "Abuja": {"latitude": 9.0765, "longitude": 7.3986},
    "Kano": {"latitude": 12.0022, "longitude": 8.5920},
    "Port Harcourt": {"latitude": 4.8156, "longitude": 7.0498},
    "Ibadan": {"latitude": 7.3775, "longitude": 3.9470},
    "Benin City": {"latitude": 6.3350, "longitude": 5.6270},
    "Kaduna": {"latitude": 10.5222, "longitude": 7.4383},
    "Enugu": {"latitude": 6.4584, "longitude": 7.5464},
    "Owerri": {"latitude": 5.4836, "longitude": 7.0333},
    "Calabar": {"latitude": 4.9517, "longitude": 8.3220},
}