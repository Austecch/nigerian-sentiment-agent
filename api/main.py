# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from api.middleware.rate_limit import limiter
from api.routes import sentiment, topics, regions, trends
from agents.orchestrator import orchestrator
from config import config

# Create FastAPI app
app = FastAPI(
    title="Nigerian Political Sentiment API",
    description=(
        "Real-time sentiment analysis of Nigerian "
        "political discourse"
    ),
    version="1.0.0",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(
    sentiment.router,
    prefix="/api/sentiment",
    tags=["Sentiment"]
)
app.include_router(
    topics.router,
    prefix="/api/topics",
    tags=["Topics"]
)
app.include_router(
    regions.router,
    prefix="/api/regions",
    tags=["Regions"]
)
app.include_router(
    trends.router,
    prefix="/api/trends",
    tags=["Trends"]
)


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": "Nigerian Political Sentiment API",
        "version": "1.0.0",
        "environment": config.ENVIRONMENT,
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "online",
        "agents": "ready",
    }


@app.post("/api/pipeline/run")
async def run_pipeline(
    max_posts: int = 50
):
    """
    Manually trigger the full pipeline run
    Scrape -> Interpret -> Aggregate
    """
    logger.info(
        f"Manual pipeline trigger: max_posts={max_posts}"
    )
    try:
        results = orchestrator.run_full_pipeline(
            max_posts_per_source=max_posts
        )
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Pipeline run failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG
    )