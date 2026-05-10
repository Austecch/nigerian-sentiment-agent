# agents/scout_agent.py
from loguru import logger
from scrapers.twitter_scraper import twitter_scraper
from scrapers.nairaland_scraper import nairaland_scraper
from scrapers.news_scraper import news_scraper
from filters.bot_detector import bot_detector
from filters.deduplication import dedup_filter
from filters.campaign_filter import campaign_filter
from database.mongodb_client import mongodb_client


class ScoutAgent:
    """
    Agent A - The Scout
    Responsible for collecting raw political
    discourse from all sources
    """

    def __init__(self):
        self.name = "Scout Agent"
        logger.info(f"{self.name} initialized")

    def collect_all_sources(
        self,
        max_posts_per_source: int = 50
    ) -> dict:
        """
        Collect posts from all three sources
        Returns cleaned and filtered posts
        """
        logger.info(
            f"{self.name}: Starting data collection "
            f"from all sources"
        )

        all_raw_posts = []

        # Collect from Twitter/X
        logger.info("Collecting from Twitter/X...")
        try:
            tweets = twitter_scraper.scrape_political_tweets(
                max_tweets=max_posts_per_source
            )
            all_raw_posts.extend(tweets)
            logger.info(f"Twitter: {len(tweets)} posts")
        except Exception as e:
            logger.error(f"Twitter collection failed: {e}")

        # Collect from Nairaland
        logger.info("Collecting from Nairaland...")
        try:
            nairaland_posts = (
                nairaland_scraper.scrape_politics_section(
                    max_posts=max_posts_per_source
                )
            )
            all_raw_posts.extend(nairaland_posts)
            logger.info(
                f"Nairaland: {len(nairaland_posts)} posts"
            )
        except Exception as e:
            logger.error(f"Nairaland collection failed: {e}")

        # Collect from News sites
        logger.info("Collecting from News sites...")
        try:
            news_posts = news_scraper.scrape_news_comments(
                max_pages=max_posts_per_source // 5
            )
            all_raw_posts.extend(news_posts)
            logger.info(
                f"News: {len(news_posts)} posts"
            )
        except Exception as e:
            logger.error(f"News collection failed: {e}")

        logger.info(
            f"Total raw posts collected: {len(all_raw_posts)}"
        )

        # Apply filters
        cleaned_posts = self._apply_filters(all_raw_posts)

        # Save to database
        if cleaned_posts:
            try:
                saved = mongodb_client.save_many_raw_posts(
                    cleaned_posts
                )
                logger.info(f"Saved {saved} posts to database")
            except Exception as e:
                logger.error(f"Database save failed: {e}")

        return {
            "total_collected": len(all_raw_posts),
            "total_clean": len(cleaned_posts),
            "posts": cleaned_posts,
        }

    def _apply_filters(self, posts: list) -> list:
        """Apply all filters to raw posts"""
        if not posts:
            return []

        logger.info(
            f"Applying filters to {len(posts)} posts"
        )

        # Step 1: Remove duplicates
        dedup_result = dedup_filter.filter_duplicates(posts)
        posts_after_dedup = dedup_result["unique_posts"]

        # Step 2: Remove bot posts
        bot_result = bot_detector.filter_posts(
            posts_after_dedup
        )
        posts_after_bot = bot_result["clean_posts"]

        # Step 3: Flag campaign posts but keep them
        campaign_result = campaign_filter.filter_campaigns(
            posts_after_bot
        )

        # Combine organic and campaign
        # but mark campaign posts
        final_posts = (
            campaign_result["organic_posts"] +
            campaign_result["campaign_posts"]
        )

        logger.info(
            f"Filtering complete: "
            f"{len(final_posts)} posts remaining "
            f"from {len(posts)} original"
        )

        return final_posts


# Single instance
scout_agent = ScoutAgent()