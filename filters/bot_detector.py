# filters/bot_detector.py
import re
from collections import Counter
from loguru import logger


class BotDetector:
    """
    Detects bot activity and coordinated
    inauthentic behavior in scraped posts
    """

    # Phrases commonly used in bot campaigns
    BOT_CAMPAIGN_PHRASES = [
        "vote for",
        "support our candidate",
        "join our movement",
        "retweet if you agree",
        "share this message",
        "copy and paste",
        "spread the word",
        "tell your friends",
    ]

    # Suspicious hashtag stuffing threshold
    MAX_HASHTAGS_BEFORE_SUSPICIOUS = 8

    # Suspicious post length threshold
    MIN_GENUINE_POST_LENGTH = 15

    def analyze_post(self, post: dict) -> dict:
        """
        Analyze a single post for bot indicators
        Returns risk level and reason
        """
        content = post.get("content", "")
        hashtags = post.get("hashtags", [])

        risk_score = 0
        reasons = []

        # Check post length
        if len(content) < self.MIN_GENUINE_POST_LENGTH:
            risk_score += 20
            reasons.append("very_short_content")

        # Check hashtag stuffing
        if len(hashtags) > self.MAX_HASHTAGS_BEFORE_SUSPICIOUS:
            risk_score += 30
            reasons.append("hashtag_stuffing")

        # Check for campaign phrases
        content_lower = content.lower()
        for phrase in self.BOT_CAMPAIGN_PHRASES:
            if phrase in content_lower:
                risk_score += 25
                reasons.append(f"campaign_phrase: {phrase}")
                break

        # Check for excessive repetition in content
        words = content_lower.split()
        if len(words) > 5:
            word_counts = Counter(words)
            most_common_count = word_counts.most_common(1)[0][1]
            if most_common_count > len(words) * 0.3:
                risk_score += 20
                reasons.append("excessive_word_repetition")

        # Check for all caps (common in bot posts)
        caps_ratio = sum(
            1 for c in content if c.isupper()
        ) / max(len(content), 1)
        if caps_ratio > 0.6 and len(content) > 20:
            risk_score += 15
            reasons.append("excessive_caps")

        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons,
        }

    def filter_posts(self, posts: list) -> dict:
        """
        Filter a list of posts removing high risk ones
        Returns clean posts and flagged posts
        """
        clean_posts = []
        flagged_posts = []

        for post in posts:
            analysis = self.analyze_post(post)
            post["bot_risk"] = analysis["risk_level"]

            if analysis["risk_level"] == "High":
                flagged_posts.append(post)
                logger.debug(
                    f"Post flagged as high bot risk: "
                    f"{analysis['reasons']}"
                )
            else:
                clean_posts.append(post)

        logger.info(
            f"Bot filter: {len(clean_posts)} clean, "
            f"{len(flagged_posts)} flagged"
        )

        return {
            "clean_posts": clean_posts,
            "flagged_posts": flagged_posts,
        }


# Single instance
bot_detector = BotDetector()