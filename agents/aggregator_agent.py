# agents/aggregator_agent.py
from collections import Counter
from loguru import logger
from database.mongodb_client import mongodb_client


class AggregatorAgent:
    """
    Agent C - The Aggregator
    Synthesizes interpreted posts into
    dashboard-ready metrics
    """

    def __init__(self):
        self.name = "Aggregator Agent"
        logger.info(f"{self.name} initialized")

    def aggregate(self, interpreted_posts: list) -> dict:
        """
        Aggregate interpreted posts into core metrics
        Returns Volume, Polarity, and Emotional Tone
        """
        if not interpreted_posts:
            logger.warning("No posts to aggregate")
            return self._empty_summary()

        logger.info(
            f"{self.name}: Aggregating "
            f"{len(interpreted_posts)} posts"
        )

        # Calculate Volume metrics
        volume = self._calculate_volume(interpreted_posts)

        # Calculate Polarity metrics
        polarity = self._calculate_polarity(
            interpreted_posts
        )

        # Calculate Emotional Tone metrics
        emotion = self._calculate_emotion(interpreted_posts)

        # Calculate Geographic distribution
        geo = self._calculate_geo_distribution(
            interpreted_posts
        )

        # Calculate Topic distribution
        topics = self._calculate_topic_distribution(
            interpreted_posts
        )

        # Calculate Bot risk
        bot_risk = self._calculate_bot_risk(
            interpreted_posts
        )

        summary = {
            "volume": volume,
            "polarity": polarity,
            "emotional_tone": emotion,
            "geographic_distribution": geo,
            "topic_distribution": topics,
            "bot_risk_summary": bot_risk,
            "total_posts_analyzed": len(interpreted_posts),
        }

        # Save summary to database
        try:
            mongodb_client.get_collection(
                "sentiment_summaries"
            ).insert_one(summary.copy())
            logger.info("Sentiment summary saved to database")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")

        return summary

    def _calculate_volume(self, posts: list) -> dict:
        """Calculate volume metrics"""
        sources = Counter(
            p.get("source", "Unknown") for p in posts
        )
        topics = Counter(
            p.get("topic", "General") for p in posts
        )

        return {
            "total_mentions": len(posts),
            "by_source": dict(sources),
            "by_topic": dict(topics),
            "top_topic": topics.most_common(1)[0][0]
            if topics else "General",
        }

    def _calculate_polarity(self, posts: list) -> dict:
        """Calculate polarity distribution"""
        polarities = Counter(
            p.get("polarity", "Neutral") for p in posts
        )
        total = len(posts)

        positive = polarities.get("Positive", 0)
        negative = polarities.get("Negative", 0)
        neutral = polarities.get("Neutral", 0)

        # Calculate average confidence
        confidence_scores = [
            p.get("confidence_score", 0.5)
            for p in posts
        ]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores else 0.5
        )

        # Determine dominant polarity
        dominant = polarities.most_common(1)[0][0] \
            if polarities else "Neutral"

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_percent": round(
                positive / total * 100, 1
            ) if total > 0 else 0,
            "negative_percent": round(
                negative / total * 100, 1
            ) if total > 0 else 0,
            "neutral_percent": round(
                neutral / total * 100, 1
            ) if total > 0 else 0,
            "dominant_polarity": dominant,
            "average_confidence": round(avg_confidence, 2),
            "sarcasm_count": sum(
                1 for p in posts
                if p.get("sarcasm_detected", False)
            ),
        }

    def _calculate_emotion(self, posts: list) -> dict:
        """Calculate emotional tone distribution"""
        emotions = Counter(
            p.get("emotional_tone", "Mixed")
            for p in posts
        )
        total = len(posts)
        dominant = emotions.most_common(1)[0][0] \
            if emotions else "Mixed"

        return {
            "hope": emotions.get("Hope", 0),
            "anger": emotions.get("Anger", 0),
            "apathy": emotions.get("Apathy", 0),
            "excitement": emotions.get("Excitement", 0),
            "mixed": emotions.get("Mixed", 0),
            "dominant_emotion": dominant,
            "hope_percent": round(
                emotions.get("Hope", 0) / total * 100, 1
            ) if total > 0 else 0,
            "anger_percent": round(
                emotions.get("Anger", 0) / total * 100, 1
            ) if total > 0 else 0,
            "apathy_percent": round(
                emotions.get("Apathy", 0) / total * 100, 1
            ) if total > 0 else 0,
            "excitement_percent": round(
                emotions.get("Excitement", 0) / total * 100, 1
            ) if total > 0 else 0,
        }

    def _calculate_geo_distribution(
        self,
        posts: list
    ) -> dict:
        """Calculate geographic distribution"""
        locations = Counter(
            p.get("location", "Unknown") for p in posts
        )
        top_locations = dict(locations.most_common(10))

        return {
            "top_locations": top_locations,
            "most_active_city": locations.most_common(1)[0][0]
            if locations else "Unknown",
        }

    def _calculate_topic_distribution(
        self,
        posts: list
    ) -> dict:
        """Calculate topic distribution"""
        topics = Counter(
            p.get("topic", "General") for p in posts
        )

        return {
            "distribution": dict(topics.most_common(10)),
            "top_topic": topics.most_common(1)[0][0]
            if topics else "General",
        }

    def _calculate_bot_risk(self, posts: list) -> dict:
        """Calculate bot risk summary"""
        risks = Counter(
            p.get("bot_or_campaign_risk", "Low")
            for p in posts
        )
        total = len(posts)

        return {
            "low_risk": risks.get("Low", 0),
            "medium_risk": risks.get("Medium", 0),
            "high_risk": risks.get("High", 0),
            "bot_risk_percent": round(
                risks.get("High", 0) / total * 100, 1
            ) if total > 0 else 0,
        }

    def _empty_summary(self) -> dict:
        """Return empty summary when no posts"""
        return {
            "volume": {"total_mentions": 0},
            "polarity": {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "dominant_polarity": "Neutral",
            },
            "emotional_tone": {
                "dominant_emotion": "Mixed"
            },
            "total_posts_analyzed": 0,
        }


# Single instance
aggregator_agent = AggregatorAgent()