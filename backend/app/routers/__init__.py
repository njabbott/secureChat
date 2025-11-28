"""API routers for Chat Magic"""

from .chat import router as chat_router
from .confluence import router as confluence_router
from .indexing import router as indexing_router

__all__ = ["chat_router", "confluence_router", "indexing_router"]
