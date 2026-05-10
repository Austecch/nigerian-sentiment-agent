# filters/deduplication.py
import hashlib
from difflib import SequenceMatcher
from loguru import logger


class DeduplicationFilter:
    """
    Removes duplicate and near-duplicate posts
    to ensure clean sentiment data
    """

    # Similarity threshold for near-duplicates
    SIMILARITY_THRESHOLD = 0.85

    def __init__(self):
        self.seen_hashes = set()
        self.seen_contents = []

    def get_content_hash(self, content: str) -> str:
        """Generate hash for exact duplicate detection"""
        normalized = " ".join(content.lower().split())
        return hashlib.md5(
            normalized.encode()
        ).hexdigest()

    def is_similar(
        self,
        content1: str,
        content2: str
    ) -> bool:
        """Check if two posts are near-duplicates"""
        similarity = SequenceMatcher(
            None,
            content1.lower(),
            content2.lower()
        ).ratio()
        return similarity >= self.SIMILARITY_THRESHOLD

    def is_duplicate(self, content: str) -> bool:
        """
        Check if content is exact or near duplicate
        Returns True if duplicate found
        """
        # Check exact duplicate
        content_hash = self.get_content_hash(content)
        if content_hash in self.seen_hashes:
            return True

        # Check near-duplicate against recent posts
        # Only check last 100 for performance
        recent_contents = self.seen_contents[-100:]
        for seen_content in recent_contents:
            if self.is_similar(content, seen_content):
                return True

        # Not a duplicate - add to seen
        self.seen_hashes.add(content_hash)
        self.seen_contents.append(content)
        return False

    def filter_duplicates(self, posts: list) -> dict:
        """
        Filter duplicates from a list of posts
        Returns unique posts and duplicate posts
        """
        # Reset for fresh batch
        self.seen_hashes = set()
        self.seen_contents = []

        unique_posts = []
        duplicate_posts = []

        for post in posts:
            content = post.get("content", "")
            if not content:
                continue

            if self.is_duplicate(content):
                post["is_duplicate"] = True
                duplicate_posts.append(post)
            else:
                post["is_duplicate"] = False
                unique_posts.append(post)

        logger.info(
            f"Deduplication: {len(unique_posts)} unique, "
            f"{len(duplicate_posts)} duplicates removed"
        )

        return {
            "unique_posts": unique_posts,
            "duplicate_posts": duplicate_posts,
        }


# Single instance
dedup_filter = DeduplicationFilter()