import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from scrapers.geo_filter import geo_filter

class NairalandScraper:
    """Scrapes political discussions from Nairaland"""

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.nairaland.com"
        self.political_keywords = [
            "tinubu", "peter obi", "atiku", "apc", "pdp", "labour party",
            "inec", "election", "government", "fuel subsidy", "economy",
            "naira", "sapa", "emilokan", "obidient", "structure", "president",
            "senator", "governor", "minister", "corruption", "budget",
            "subsidy", "dollar", "inflation", "security", "bandit", "kidnap",
            "boko haram", "senate", "house of reps", "constitution", "vote",
            "pvc", "renewed hope", "niger delta", "arewa", "ohanaeze",
            "afenifere", "middle belt", "northern", "tinubu's", "obi's",
        ]

    def scrape_politics_section(self, max_posts=50):
        logger.info(f"Starting Nairaland scrape - max posts: {max_posts}")
        scraped_posts = []
        try:
            r = self.scraper.get(f"{self.base_url}/politics", timeout=15)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, "html.parser")
            thread_urls = []
            for a in soup.select("a[href]"):
                href = a.get("href", "")
                parts = href.strip("/").split("/")
                if len(parts) == 2 and parts[0].isdigit() and href not in thread_urls:
                    thread_urls.append(href)
            logger.info(f"Found {len(thread_urls)} threads")
            for thread_path in thread_urls[:max_posts]:
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

    def _scrape_thread(self, thread_path):
        posts = []
        try:
            url = f"{self.base_url}{thread_path}"
            r = self.scraper.get(url, timeout=15)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select("table tr")
            for row in rows:
                cells = row.select("td")
                if len(cells) < 2:
                    continue
                content_td = cells[1]
                content = content_td.get_text(strip=True)
                if len(content) < 30:
                    continue
                author_td = cells[0]
                author = author_td.get_text(strip=True).split("\n")[0][:50] if author_td else "Unknown"
                if self._is_political(content):
                    processed = self._process_post({
                        "content": content, "author": author, "url": url,
                    })
                    if processed:
                        posts.append(processed)
            return posts
        except Exception as e:
            logger.error(f"Thread scrape failed: {e}")
            return []

    def _process_post(self, raw_post):
        try:
            content = raw_post.get("content", "")
            if not content or len(content) < 20:
                return None
            return {
                "source": "Nairaland",
                "content": content[:2000],
                "author": raw_post.get("author", "Unknown")[:50],
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

    def _is_political(self, content):
        return any(kw in content.lower() for kw in self.political_keywords)

nairaland_scraper = NairalandScraper()
