"""Chat-related data models"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PIIInfo(BaseModel):
    """Information about detected and filtered PII"""

    total_count: int = Field(default=0, description="Total number of PII items detected")
    entities: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each PII entity type (e.g., {'PERSON': 2, 'EMAIL': 1})",
    )


class ChatMessage(BaseModel):
    """User message sent to the chatbot"""

    message: str = Field(..., description="The user's message/question")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking conversations")


class ChatResponse(BaseModel):
    """Response from the chatbot"""

    response: str = Field(..., description="The chatbot's response")
    sources: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Source documents used to generate the response",
    )
    pii_filtered: bool = Field(default=False, description="Whether PII was filtered from the query")
    pii_info: Optional[PIIInfo] = Field(None, description="Information about filtered PII")
    session_id: Optional[str] = Field(None, description="Session ID for this conversation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ChatHistory(BaseModel):
    """Chat history entry"""

    id: int
    session_id: str
    user_message: str
    bot_response: str
    pii_filtered: bool
    timestamp: datetime
