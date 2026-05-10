# filters/campaign_filter.py
from loguru import logger


class CampaignFilter:
    """
    Identifies and filters coordinated
    campaign messaging from organic sentiment
    """

    CAMPAIGN_INDICATORS = [
        "vote for",
        "support",
        "join us",
        "together we",
        "our candidate",
        "our party",
        "we must",
        "don't forget to vote",
        "election day",
        "polling unit",
        "get your pvc",
        "collect your pvc",
    ]

    def is_campaign_content(self, content: str) -> bool:
        """Check if content is campaign messaging"""
        content_lower = content.lower()
        matches = sum(
            1 for indicator in self.CAMPAIGN_INDICATORS
            if indicator in content_lower
        )
        return matches >= 2

    def filter_campaigns(self, posts: list) -> dict:
        """Separate campaign posts from organic posts"""
        organic_posts = []
        campaign_posts = []

        for post in posts:
            content = post.get("content", "")
            if self.is_campaign_content(content):
                post["bot_or_campaign_risk"] = "High"
                campaign_posts.append(post)
            else:
                organic_posts.append(post)

        logger.info(
            f"Campaign filter: {len(organic_posts)} organic, "
            f"{len(campaign_posts)} campaign posts"
        )

        return {
            "organic_posts": organic_posts,
            "campaign_posts": campaign_posts,
        }


# Single instance
campaign_filter = CampaignFilter()