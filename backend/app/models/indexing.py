"""Indexing-related data models"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class IndexingStatusEnum(str, Enum):
    """Indexing status enumeration"""

    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IndexingProgress(BaseModel):
    """Real-time indexing progress information"""

    status: IndexingStatusEnum = Field(..., description="Current indexing status")
    current_space: Optional[str] = Field(None, description="Currently indexing space")
    total_spaces: int = Field(default=0, description="Total number of spaces to index")
    processed_spaces: int = Field(default=0, description="Number of spaces processed")
    total_documents: int = Field(default=0, description="Total documents to index")
    processed_documents: int = Field(default=0, description="Number of documents processed")
    current_message: Optional[str] = Field(None, description="Current progress message")
    error_message: Optional[str] = Field(None, description="Error message if status is FAILED")
    total_pii_filtered: int = Field(default=0, description="Total PII items filtered")
    pii_by_type: Dict[str, int] = Field(default_factory=dict, description="PII counts by type")


class IndexingStatus(BaseModel):
    """Indexing status and metadata"""

    last_indexed: Optional[datetime] = Field(None, description="Last successful indexing timestamp")
    is_indexing: bool = Field(default=False, description="Whether indexing is currently in progress")
    total_documents: int = Field(default=0, description="Total documents in vector database")
    total_spaces: int = Field(default=0, description="Total spaces indexed")
    next_scheduled_run: Optional[datetime] = Field(None, description="Next scheduled indexing run")
    progress: Optional[IndexingProgress] = Field(None, description="Current indexing progress if in progress")
    last_pii_filtered: int = Field(default=0, description="Total PII items filtered in last indexing")
    last_pii_by_type: Dict[str, int] = Field(default_factory=dict, description="PII counts by type from last indexing")
