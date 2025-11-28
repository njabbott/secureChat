"""Data models for Chat Magic"""

from .chat import ChatMessage, ChatResponse, PIIInfo
from .confluence import ConfluenceSpace, ConfluenceDocument
from .indexing import IndexingStatus, IndexingProgress

__all__ = [
    "ChatMessage",
    "ChatResponse",
    "PIIInfo",
    "ConfluenceSpace",
    "ConfluenceDocument",
    "IndexingStatus",
    "IndexingProgress",
]
