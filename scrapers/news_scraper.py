import cloudscraper
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from scrapers.geo_filter import geo_filter

class NewsScraper:
    """Scrapes headlines + article text from Nigerian news sites"""

    def __init__(self):
        self.news_sources = [
            {
                "name": "Punch",
                "url": "https://punchng.com/topics/politics/",
                "selector": ".entry-title a",
                "body_selector": ".post-content",
                "uses_cloudscraper": False,
            },
            {
                "name": "Vanguard",
                "url": "https://www.vanguardngr.com/category/politics/",
                "selector": ".entry-title a",
                "body_selector": "#content",
                "uses_cloudscraper": True,
            },
            {
                "name": "Premium Times",
                "url": "https://www.premiumtimesng.com/category/news/politics-news/",
                "selector": ".jeg_post_title a",
                "body_selector": None,
                "uses_cloudscraper": False,
            },
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.scraper = cloudscraper.create_scraper()

    def scrape_news_comments(self, max_pages: int = 20) -> list:
        logger.info(f"Starting news scrape - max articles: {max_pages}")
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

    def _fetch(self, url: str, use_cloudscraper: bool = False) -> str | None:
        try:
            if use_cloudscraper:
                r = self.scraper.get(url, timeout=15)
            else:
                r = requests.get(url, headers=self.headers, timeout=15)
            r.encoding = "utf-8"
            return r.text if r.status_code == 200 else None
        except Exception as e:
            logger.warning(f"Fetch failed for {url}: {e}")
            return None

    def _fetch_article_body(self, url: str, source: dict) -> str:
        html = self._fetch(url, source.get("uses_cloudscraper", False))
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        body_sel = source.get("body_selector")
        if body_sel:
            container = soup.select_one(body_sel)
            if container:
                paras = container.find_all("p")
                text = " ".join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 20)
                if len(text) > 100:
                    return text[:2000]
        return ""

    def _scrape_source(self, source: dict, max_pages: int = 20) -> list:
        html = self._fetch(source["url"], source.get("uses_cloudscraper", False))
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        seen_urls = set()
        articles = []

        for link in soup.select(source["selector"]):
            href = link.get("href", "").strip()
            title = link.get_text(strip=True)
            if not href or len(title) < 20 or href in seen_urls:
                continue
            seen_urls.add(href)
            if href.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(source["url"])
                href = f"{parsed.scheme}://{parsed.netloc}{href}"

            body_text = self._fetch_article_body(href, source)

            processed = self._process_article({
                "title": title,
                "url": href,
                "text": body_text or title,
            }, source["name"])
            if processed:
                articles.extend(processed)

            if len(articles) >= max_pages:
                break

        return articles[:max_pages]

    def _process_article(self, raw_article: dict, source_name: str) -> list:
        try:
            title = raw_article.get("title", "")
            text = raw_article.get("text", "")
            url = raw_article.get("url", "")
            if len(title) < 15:
                return []
            content = f"{title}. {text[:1500]}"
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
