# scrapers/twitter_scraper.py
from apify_client import ApifyClient
from datetime import datetime
from loguru import logger
from config import config
from scrapers.geo_filter import geo_filter


class TwitterScraper:
    """Scrapes Nigerian political tweets via Apify"""

    def __init__(self):
        self.client = ApifyClient(config.APIFY_API_KEY)
        self.political_hashtags = [
            "#Nigeria",
            "#NigeriaDecides",
            "#APC",
            "#PDP",
            "#LabourParty",
            "#Tinubu",
            "#PeterObi",
            "#Atiku",
            "#NigeriaElection",
            "#NigeriaGovernment",
            "#FuelSubsidy",
            "#NigeriaEconomy",
            "#Naira",
            "#Sapa",
            "#Emilokan",
            "#Obidient",
        ]

    def scrape_political_tweets(
        self,
        max_tweets: int = 100
    ) -> list:
        """
        Scrape Nigerian political tweets using Apify
        Twitter scraper actor
        """
        logger.info(
            f"Starting Twitter scrape - "
            f"max tweets: {max_tweets}"
        )

        all_tweets = []

        try:
            # Build search queries
            search_terms = " OR ".join(
                self.political_hashtags[:8]
            )

            run_input = {
                "searchTerms": [
                    search_terms,
                    "Nigeria politics",
                    "Nigerian government",
                ],
                "maxTweets": max_tweets,
                "addUserInfo": True,
                "startUrls": [],
                "lang": "",
                # Empty to get all languages
            }

            # Run Apify Twitter scraper
            run = self.client.actor(
                "quacker/twitter-scraper"
            ).call(run_input=run_input)

            # Get results
            dataset_items = self.client.dataset(
                run["defaultDatasetId"]
            ).iterate_items()

            for tweet in dataset_items:
                processed = self._process_tweet(tweet)
                if processed:
                    all_tweets.append(processed)

            logger.info(
                f"Twitter scrape complete: "
                f"{len(all_tweets)} tweets"
            )
            return all_tweets

        except Exception as e:
            logger.error(f"Twitter scraping failed: {e}")
            return []

    def _process_tweet(self, raw_tweet: dict) -> dict:
        """Process and structure a raw tweet"""
        try:
            content = raw_tweet.get("text", "")
            if not content or len(content) < 10:
                return None

            # Get user location if available
            user_info = raw_tweet.get("user", {})
            profile_location = user_info.get(
                "location", ""
            )

            # Detect Nigerian location
            location = geo_filter.detect_location(
                content,
                profile_location
            )

            # Extract hashtags
            hashtags = []
            entities = raw_tweet.get("entities", {})
            if entities:
                hashtag_list = entities.get("hashtags", [])
                hashtags = [
                    f"#{h.get('text', '')}"
                    for h in hashtag_list
                ]

            # Get timestamp
            created_at = raw_tweet.get("created_at")
            timestamp = datetime.utcnow()
            if created_at:
                try:
                    timestamp = datetime.strptime(
                        created_at,
                        "%a %b %d %H:%M:%S +0000 %Y"
                    )
                except Exception:
                    timestamp = datetime.utcnow()

            return {
                "source": "X",
                "content": content,
                "author": user_info.get(
                    "screen_name", "Unknown"
                ),
                "url": (
                    f"https://twitter.com/i/web/status/"
                    f"{raw_tweet.get('id_str', '')}"
                ),
                "location": location,
                "hashtags": hashtags,
                "timestamp": timestamp,
                "scraped_at": datetime.utcnow(),
                "is_duplicate": False,
                "bot_risk": "Low",
                "retweet_count": raw_tweet.get(
                    "retweet_count", 0
                ),
                "like_count": raw_tweet.get(
                    "favorite_count", 0
                ),
            }

        except Exception as e:
            logger.error(f"Tweet processing failed: {e}")
            return None


# Single instance to use across project
twitter_scraper = TwitterScraper()