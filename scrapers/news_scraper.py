# scrapers/news_scraper.py
from apify_client import ApifyClient
from datetime import datetime
from loguru import logger
from config import config
from scrapers.geo_filter import geo_filter


class NewsScraper:
    """Scrapes comments from Nigerian news websites"""

    def __init__(self):
        self.client = ApifyClient(config.APIFY_API_KEY)
        self.news_sources = [
            {
                "name": "Punch",
                "url": "https://punchng.com/topics/politics/",
            },
            {
                "name": "Vanguard",
                "url": (
                    "https://www.vanguardngr.com/category"
                    "/politics/"
                ),
            },
            {
                "name": "ThisDay",
                "url": (
                    "https://www.thisdaylive.com/index.php"
                    "/category/politics/"
                ),
            },
            {
                "name": "Premium Times",
                "url": (
                    "https://www.premiumtimesng.com"
                    "/category/news/politics-news/"
                ),
            },
        ]

    def scrape_news_comments(
        self,
        max_pages: int = 20
    ) -> list:
        """
        Scrape comments from Nigerian news websites
        """
        logger.info(
            f"Starting news comment scrape - "
            f"max pages: {max_pages}"
        )

        all_comments = []

        for source in self.news_sources:
            try:
                comments = self._scrape_source(
                    source,
                    max_pages
                )
                all_comments.extend(comments)
                logger.info(
                    f"Scraped {len(comments)} comments "
                    f"from {source['name']}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to scrape {source['name']}: {e}"
                )
                continue

        logger.info(
            f"News scrape complete: "
            f"{len(all_comments)} total comments"
        )
        return all_comments

    def _scrape_source(
        self,
        source: dict,
        max_pages: int
    ) -> list:
        """Scrape a single news source"""
        try:
            run_input = {
                "startUrls": [{"url": source["url"]}],
                "maxCrawlPages": max_pages,
                "maxCrawlDepth": 2,
            }

            run = self.client.actor(
                "apify/website-content-crawler"
            ).call(run_input=run_input)

            items = list(
                self.client.dataset(
                    run["defaultDatasetId"]
                ).iterate_items()
            )

            comments = []
            for item in items:
                processed = self._process_article(
                    item,
                    source["name"]
                )
                if processed:
                    comments.extend(processed)

            return comments

        except Exception as e:
            logger.error(
                f"Source scraping failed "
                f"for {source['name']}: {e}"
            )
            return []

    def _process_article(
        self,
        raw_article: dict,
        source_name: str
    ) -> list:
        """Extract comments from a news article"""
        processed_comments = []

        try:
            # Get article text as comment context
            text = raw_article.get("text", "")
            url = raw_article.get("url", "")
            title = raw_article.get("title", "")

            if text and len(text) > 50:
                # Use article title and snippet as content
                content = f"{title}. {text[:500]}"

                processed_comments.append({
                    "source": "NewsComment",
                    "content": content,
                    "author": source_name,
                    "url": url,
                    "location": geo_filter.detect_location(
                        content
                    ),
                    "hashtags": [],
                    "timestamp": datetime.utcnow(),
                    "scraped_at": datetime.utcnow(),
                    "is_duplicate": False,
                    "bot_risk": "Low",
                    "news_source": source_name,
                })

        except Exception as e:
            logger.error(f"Article processing failed: {e}")

        return processed_comments


# Single instance to use across project
news_scraper = NewsScraper()