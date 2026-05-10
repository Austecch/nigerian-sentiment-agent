import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from scrapers.geo_filter import geo_filter

class NewsScraper:
    """Scrapes headlines from Nigerian news sites using requests + BeautifulSoup"""

    def __init__(self):
        self.news_sources = [
            {"name": "Punch", "url": "https://punchng.com/topics/politics/"},
            {"name": "Vanguard", "url": "https://www.vanguardngr.com/category/politics/"},
            {"name": "Premium Times", "url": "https://www.premiumtimesng.com/category/news/politics-news/"},
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_news_comments(self, max_pages: int = 20) -> list:
        logger.info(f"Starting news scrape - max pages: {max_pages}")
        all_articles = []

        for source in self.news_sources:
            try:
                articles = self._scrape_source(source, max_pages)
                all_articles.extend(articles)
                logger.info(f"Got {len(articles)} articles from {source['name']}")
            except Exception as e:
                logger.error(f"Failed to scrape {source['name']}: {e}")

        logger.info(f"News scrape complete: {len(all_articles)} total articles")
        return all_articles

    def _scrape_source(self, source: dict, max_pages: int = 20) -> list:
        articles = []
        r = requests.get(source["url"], headers=self.headers, timeout=15)
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            title = link.get_text(strip=True)
            if len(title) < 30:
                continue

            processed = self._process_article({
                "title": title,
                "url": href if href.startswith("http") else source["url"] + href,
                "text": title,
            }, source["name"])
            if processed:
                articles.extend(processed)

        return articles[:max_pages]

    def _process_article(self, raw_article: dict, source_name: str) -> list:
        try:
            title = raw_article.get("title", "")
            text = raw_article.get("text", "")
            url = raw_article.get("url", "")
            content = f"{title}. {text[:500]}"
            if len(content) < 50:
                return []
            return [{
                "source": "NewsComment",
                "content": content,
                "author": source_name,
                "url": url,
                "location": geo_filter.detect_location(content),
                "hashtags": [],
                "timestamp": datetime.utcnow(),
                "scraped_at": datetime.utcnow(),
                "is_duplicate": False,
                "bot_risk": "Low",
                "news_source": source_name,
            }]
        except Exception as e:
            logger.error(f"Article processing failed: {e}")
            return []

news_scraper = NewsScraper()
