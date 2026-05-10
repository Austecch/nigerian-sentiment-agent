# scrapers/nairaland_scraper.py
from apify_client import ApifyClient
from datetime import datetime
from loguru import logger
from config import config
from scrapers.geo_filter import geo_filter


class NairalandScraper:
    """Scrapes political discussions from Nairaland"""

    def __init__(self):
        self.client = ApifyClient(config.APIFY_API_KEY)
        self.political_sections = [
            "politics",
            "news",
            "crime",
        ]
        self.political_keywords = [
            "tinubu", "peter obi", "atiku",
            "apc", "pdp", "labour party",
            "inec", "election", "government",
            "fuel subsidy", "economy", "naira",
            "sapa", "emilokan", "obidient",
            "structure", "president", "senator",
            "governor", "minister", "corruption",
        ]

    def scrape_politics_section(
        self,
        max_posts: int = 50
    ) -> list:
        """
        Scrape political posts from Nairaland
        using Apify web scraper
        """
        logger.info(
            f"Starting Nairaland scrape - max posts: {max_posts}"
        )

        scraped_posts = []

        try:
            # Use Apify's website content crawler
            run_input = {
                "startUrls": [
                    {
                        "url": (
                            "https://www.nairaland.com/politics"
                        )
                    },
                    {
                        "url": (
                            "https://www.nairaland.com/news"
                        )
                    },
                ],
                "maxCrawlPages": max_posts,
                "maxCrawlDepth": 2,
                "linkSelector": "a[href]",
                "pageFunction": """
                async function pageFunction(context) {
                    const { page, request } = context;
                    const url = request.url;

                    // Extract post content from Nairaland
                    const posts = await page.evaluate(() => {
                        const results = [];
                        const postDivs = document.querySelectorAll(
                            '.narrow'
                        );

                        postDivs.forEach(div => {
                            const content = div.innerText;
                            const links = div.querySelectorAll('a');
                            let author = 'Unknown';

                            if (links.length > 0) {
                                author = links[0].innerText;
                            }

                            if (content && content.length > 20) {
                                results.push({
                                    content: content.trim(),
                                    author: author,
                                    url: window.location.href
                                });
                            }
                        });
                        return results;
                    });

                    return posts;
                }
                """,
            }

            # Run the Apify actor
            run = self.client.actor(
                "apify/website-content-crawler"
            ).call(run_input=run_input)

            # Get results from dataset
            dataset_items = self.client.dataset(
                run["defaultDatasetId"]
            ).iterate_items()

            for item in dataset_items:
                if isinstance(item, list):
                    for post in item:
                        processed = self._process_post(post)
                        if processed:
                            scraped_posts.append(processed)
                elif isinstance(item, dict):
                    processed = self._process_post(item)
                    if processed:
                        scraped_posts.append(processed)

            logger.info(
                f"Nairaland scrape complete: "
                f"{len(scraped_posts)} posts"
            )
            return scraped_posts

        except Exception as e:
            logger.error(f"Nairaland scraping failed: {e}")
            return []

    def _process_post(self, raw_post: dict) -> dict:
        """Process and structure a raw Nairaland post"""
        try:
            content = raw_post.get("content", "")
            if not content or len(content) < 20:
                return None

            # Check if content is political
            if not self._is_political(content):
                return None

            return {
                "source": "Nairaland",
                "content": content[:2000],
                # Limit content length
                "author": raw_post.get("author", "Unknown"),
                "url": raw_post.get("url", ""),
                "location": geo_filter.detect_location(content),
                "hashtags": [],
                "timestamp": datetime.utcnow(),
                "scraped_at": datetime.utcnow(),
                "is_duplicate": False,
                "bot_risk": "Low",
            }
        except Exception as e:
            logger.error(f"Post processing failed: {e}")
            return None

    def _is_political(self, content: str) -> bool:
        """Check if content contains political keywords"""
        content_lower = content.lower()
        for keyword in self.political_keywords:
            if keyword in content_lower:
                return True
        return False


# Single instance to use across project
nairaland_scraper = NairalandScraper()