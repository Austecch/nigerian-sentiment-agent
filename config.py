# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Apify
    APIFY_API_KEY = os.getenv("APIFY_API_KEY")

    # MongoDB
    MONGODB_CONNECTION_STRING = os.getenv(
        "MONGODB_CONNECTION_STRING"
    )
    MONGODB_DATABASE_NAME = os.getenv(
        "MONGODB_DATABASE_NAME",
        "nigerian_sentiment_db"
    )

    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv(
        "PINECONE_INDEX_NAME",
        "nigerian-sentiment-index"
    )

    # API Settings
    API_SECRET_KEY = os.getenv(
        "API_SECRET_KEY",
        "nigerian-sentiment-super-secret-key-2024"
    )
    API_ALGORITHM = os.getenv("API_ALGORITHM", "HS256")
    API_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    # Scraping Settings
    SCRAPING_INTERVAL_MINUTES = int(
        os.getenv("SCRAPING_INTERVAL_MINUTES", 30)
    )
    MAX_POSTS_PER_SCRAPE = int(
        os.getenv("MAX_POSTS_PER_SCRAPE", 100)
    )
    GEO_LOCATIONS = os.getenv(
        "GEO_LOCATIONS",
        "Lagos,Abuja,Kano,Port Harcourt"
    ).split(",")

    # Political Hashtags
    POLITICAL_HASHTAGS = os.getenv(
        "POLITICAL_HASHTAGS",
        "#Nigeria,#NigeriaDecides,#APC,#PDP"
    ).split(",")

    # Dashboard Settings
    DASHBOARD_REFRESH_INTERVAL = int(
        os.getenv("DASHBOARD_REFRESH_INTERVAL", 300)
    )
    MAX_DISPLAY_POSTS = int(
        os.getenv("MAX_DISPLAY_POSTS", 1000)
    )

    # Deployment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    PORT = int(os.getenv("PORT", 8000))

    @classmethod
    def validate(cls):
        """Validate all required environment variables"""
        required_keys = [
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            ("APIFY_API_KEY", cls.APIFY_API_KEY),
            (
                "MONGODB_CONNECTION_STRING",
                cls.MONGODB_CONNECTION_STRING
            ),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
        ]

        missing = []
        for key_name, key_value in required_keys:
            if not key_value:
                missing.append(key_name)

        if missing:
            raise ValueError(
                f"Missing required environment variables: "
                f"{', '.join(missing)}"
            )

        return True


# ✅ THIS LINE IS CRITICAL - creates the config instance
config = Config()