"""Main FastAPI application for Chat Magic"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
)
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
    logger.info("Starting Chat Magic application...")

    # Initialize services
    confluence_svc = ConfluenceService()
    vector_db_svc = VectorDBService()
    openai_svc = OpenAIService()
    pii_svc = PIIService()
    indexing_svc = IndexingService(confluence_svc, vector_db_svc, pii_svc)

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

    # Set up scheduled indexing
    scheduler.add_job(
        indexing_svc.start_indexing,
        "interval",
        hours=settings.indexing_schedule_hours,
        id="scheduled_indexing",
        replace_existing=True,
    )
    scheduler.start()

    logger.info(
        f"Scheduled indexing every {settings.indexing_schedule_hours} hours"
    )
    logger.info("Chat Magic application started successfully")

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
