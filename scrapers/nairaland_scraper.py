import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from scrapers.geo_filter import geo_filter

class NairalandScraper:
    """Scrapes political discussions from Nairaland using requests + BeautifulSoup"""

    def __init__(self):
        self.base_url = "https://www.nairaland.com"
        self.political_keywords = [
            "tinubu", "peter obi", "atiku",
            "apc", "pdp", "labour party",
            "inec", "election", "government",
            "fuel subsidy", "economy", "naira",
            "sapa", "emilokan", "obidient",
            "structure", "president", "senator",
            "governor", "minister", "corruption",
            "budget", "subsidy", "dollar", "inflation",
            "security", "bandit", "kidnap", "boko haram",
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_politics_section(self, max_posts: int = 50) -> list:
        logger.info(f"Starting Nairaland scrape - max posts: {max_posts}")
        scraped_posts = []

        try:
            r = requests.get(f"{self.base_url}/politics", headers=self.headers, timeout=15)
            if r.status_code != 200:
                logger.error(f"Nairaland returned status {r.status_code}")
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select("a[href*='/politics/']")
            thread_urls = list(dict.fromkeys([
                a["href"] for a in links
                if a["href"].startswith("/politics/") and a["href"].count("/") == 2
            ]))

            logger.info(f"Found {len(thread_urls)} threads")

            for i, thread_path in enumerate(thread_urls[:max_posts]):
                posts = self._scrape_thread(thread_path)
                scraped_posts.extend(posts)
                if len(scraped_posts) >= max_posts:
                    break

            scraped_posts = scraped_posts[:max_posts]
            logger.info(f"Nairaland scrape complete: {len(scraped_posts)} posts")
            return scraped_posts

        except Exception as e:
            logger.error(f"Nairaland scraping failed: {e}")
            return []

    def _scrape_thread(self, thread_path: str) -> list:
        posts = []
        try:
            url = f"{self.base_url}{thread_path}" if thread_path.startswith("/") else thread_path
            r = requests.get(url, headers=self.headers, timeout=15)
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            post_divs = soup.select("td[colspan='2']")

            for div in post_divs[:3]:
                text = div.get_text(strip=True)
                if len(text) < 30:
                    continue

                author_tag = div.find_previous("a", class_="user")
                author = author_tag.get_text(strip=True) if author_tag else "Unknown"

                if self._is_political(text):
                    processed = self._process_post({
                        "content": text,
                        "author": author,
                        "url": url,
                    })
                    if processed:
                        posts.append(processed)

        except Exception as e:
            logger.error(f"Thread scrape failed for {thread_path}: {e}")

        return posts

    def _process_post(self, raw_post: dict) -> dict:
        try:
            content = raw_post.get("content", "")
            if not content or len(content) < 20:
                return None
            if not self._is_political(content):
                return None
            return {
                "source": "Nairaland",
                "content": content[:2000],
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
        content_lower = content.lower()
        return any(kw in content_lower for kw in self.political_keywords)

nairaland_scraper = NairalandScraper()
