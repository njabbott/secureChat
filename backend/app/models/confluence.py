"""Confluence-related data models"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConfluenceSpace(BaseModel):
    """Confluence space information"""

    key: str = Field(..., description="Space key")
    name: str = Field(..., description="Space name")
    document_count: int = Field(default=0, description="Number of documents in this space")
    type: Optional[str] = Field(None, description="Space type (global, personal)")
    url: Optional[str] = Field(None, description="URL to the space")


class ConfluenceDocument(BaseModel):
    """Confluence document/page"""

    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    space_key: str = Field(..., description="Space key this document belongs to")
    space_name: str = Field(..., description="Space name")
    content: str = Field(..., description="Document content (text)")
    url: str = Field(..., description="URL to the document")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    modified: Optional[datetime] = Field(None, description="Last modification timestamp")
    author: Optional[str] = Field(None, description="Document author")
