"""Rate limiting models and configuration"""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field


@dataclass
class RateLimitConfig:
    """Configuration for a specific endpoint's rate limit"""
    requests: int  # Maximum number of requests allowed
    window_seconds: int  # Time window in seconds

    @property
    def requests_per_minute(self) -> float:
        """Calculate requests per minute for this configuration"""
        return (self.requests / self.window_seconds) * 60


class RateLimitInfo(BaseModel):
    """Rate limit information returned in headers and error responses"""
    limit: int = Field(..., description="Maximum number of requests allowed in the window")
    remaining: int = Field(..., description="Number of requests remaining in current window")
    reset: int = Field(..., description="Unix timestamp when the rate limit resets")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying (only present on 429 responses)")
