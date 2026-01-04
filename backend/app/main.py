"""Main FastAPI application for Chat Magic"""

import logging
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import settings
from .logging_config import setup_logging
from .services import (
    ConfluenceService,
    VectorDBService,
    OpenAIService,
    PIIService,
    IndexingService,
    RateLimitService,
)
from .middleware import RateLimitMiddleware
from .models.rate_limit import RateLimitConfig
from .routers import chat, confluence, indexing

# Configure logging
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("="*60)
    logger.info("Starting Chat Magic application...")
    logger.info("="*60)

    # Initialize services
    logger.info("→ Initializing Confluence service...")
    confluence_svc = ConfluenceService()
    logger.info("✓ Confluence service initialized")

    logger.info("→ Initializing VectorDB service...")
    vector_db_svc = VectorDBService()
    logger.info("✓ VectorDB service initialized")

    logger.info("→ Initializing OpenAI service...")
    openai_svc = OpenAIService()
    logger.info("✓ OpenAI service initialized")

    logger.info("→ Initializing PII service (loading spaCy model)...")
    pii_svc = PIIService()
    logger.info("✓ PII service initialized")

    logger.info("→ Initializing Indexing service...")
    indexing_svc = IndexingService(confluence_svc, vector_db_svc, pii_svc)
    logger.info("✓ Indexing service initialized")

    logger.info("→ Initializing Rate Limit service...")
    rate_limit_svc = RateLimitService()

    # Register endpoint limits
    rate_limit_svc.register_endpoint(
        "/api/chat/message",
        RateLimitConfig(
            requests=settings.rate_limit_chat_requests,
            window_seconds=settings.rate_limit_chat_window
        )
    )
    rate_limit_svc.register_endpoint(
        "/api/indexing/start",
        RateLimitConfig(
            requests=settings.rate_limit_indexing_requests,
            window_seconds=settings.rate_limit_indexing_window
        )
    )

    logger.info("✓ Rate Limit service initialized")

    # Inject services into routers
    chat.vector_db_service = vector_db_svc
    chat.openai_service = openai_svc
    chat.pii_service = pii_svc

    confluence.confluence_service = confluence_svc
    confluence.vector_db_service = vector_db_svc

    indexing.indexing_service = indexing_svc

    # Store services in app state for access elsewhere
    app.state.confluence_service = confluence_svc
    app.state.vector_db_service = vector_db_svc
    app.state.openai_service = openai_svc
    app.state.pii_service = pii_svc
    app.state.indexing_service = indexing_svc
    app.state.rate_limit_service = rate_limit_svc

    # Set up scheduled indexing
    scheduler.add_job(
        indexing_svc.start_indexing,
        "interval",
        hours=settings.indexing_schedule_hours,
        id="scheduled_indexing",
        replace_existing=True,
    )

    # Set up rate limit cleanup
    scheduler.add_job(
        lambda: asyncio.create_task(rate_limit_svc.cleanup_stale_buckets()),
        "interval",
        seconds=settings.rate_limit_cleanup_interval,
        id="rate_limit_cleanup",
        replace_existing=True,
    )

    scheduler.start()

    logger.info(f"→ Scheduled indexing every {settings.indexing_schedule_hours} hours")
    logger.info(f"→ Scheduled rate limit cleanup every {settings.rate_limit_cleanup_interval} seconds")
    logger.info("="*60)
    logger.info("✓✓✓ Chat Magic application started successfully! ✓✓✓")
    logger.info(f"✓✓✓ Server listening on {settings.host}:{settings.port} ✓✓✓")
    logger.info("="*60)

    yield

    # Shutdown
    logger.info("Shutting down Chat Magic application...")
    scheduler.shutdown()
    logger.info("Chat Magic application stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-based chatbot for searching Confluence documentation with PII protection",
    lifespan=lifespan,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming HTTP requests"""
    start_time = time.time()

    # Log incoming request
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"→ HTTP {request.method} {request.url.path} from {client_host}")

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(f"← HTTP {request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")

    return response


# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    enabled=settings.rate_limit_enabled
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(confluence.router)
app.include_router(indexing.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "Welcome to Chat Magic! Access the API docs at /docs",
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "name": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
