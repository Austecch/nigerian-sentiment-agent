# api/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SentimentResponse(BaseModel):
    """Response schema for sentiment data"""
    source: str
    location: str
    content: str
    topic: str
    polarity: str
    emotional_tone: str
    target_of_sentiment: str
    sarcasm_detected: bool
    bot_or_campaign_risk: str
    confidence_score: float
    explanation: Optional[str] = None
    interpreted_at: Optional[datetime] = None


class VolumeMetrics(BaseModel):
    """Volume metrics schema"""
    total_mentions: int
    by_source: dict
    by_topic: dict
    top_topic: str


class PolarityMetrics(BaseModel):
    """Polarity metrics schema"""
    positive: int
    negative: int
    neutral: int
    positive_percent: float
    negative_percent: float
    neutral_percent: float
    dominant_polarity: str
    average_confidence: float
    sarcasm_count: int


class EmotionMetrics(BaseModel):
    """Emotional tone metrics schema"""
    hope: int
    anger: int
    apathy: int
    excitement: int
    mixed: int
    dominant_emotion: str
    hope_percent: float
    anger_percent: float
    apathy_percent: float
    excitement_percent: float


class DashboardSummary(BaseModel):
    """Complete dashboard summary schema"""
    volume: VolumeMetrics
    polarity: PolarityMetrics
    emotional_tone: EmotionMetrics
    total_posts_analyzed: int


class PipelineRunResponse(BaseModel):
    """Response from running the full pipeline"""
    pipeline_status: str
    total_collected: Optional[int] = 0
    total_clean: Optional[int] = 0
    interpreted_count: Optional[int] = 0
    errors: Optional[List[str]] = []


class RegionData(BaseModel):
    """Geographic region sentiment data"""
    location: str
    mention_count: int
    dominant_sentiment: str
    dominant_emotion: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TopicTrend(BaseModel):
    """Topic trend data"""
    topic: str
    mention_count: int
    positive_percent: float
    negative_percent: float
    dominant_emotion: str