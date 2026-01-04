"""Rate limiting middleware for FastAPI"""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits on API endpoints

    Intercepts requests, checks rate limits, and returns 429 responses
    when limits are exceeded. Adds X-RateLimit-* headers to all responses.
    """

    def __init__(self, app, enabled: bool = True):
        """
        Initialize rate limit middleware

        Args:
            app: FastAPI application instance
            enabled: Whether rate limiting is enabled (default: True)
        """
        super().__init__(app)
        self.enabled = enabled
        logger.info(f"RateLimitMiddleware initialized (enabled={enabled})")

    def _get_rate_limit_service(self, request: Request):
        """Get rate limit service from app state"""
        return getattr(request.app.state, 'rate_limit_service', None)

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limits

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response (429 if rate limited, otherwise normal response)
        """
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        # Get rate limit service
        rate_limit_service = self._get_rate_limit_service(request)
        if not rate_limit_service:
            logger.warning("Rate limit service not available, allowing request")
            return await call_next(request)

        # Get client identifier and endpoint
        client_key = self._get_client_key(request)
        endpoint = request.url.path

        # Check rate limit
        allowed, info = await rate_limit_service.check_rate_limit(client_key, endpoint)

        # If rate limited, return 429
        if not allowed and info:
            logger.warning(
                f"Rate limit exceeded for {client_key} on {endpoint}. "
                f"Retry after {info.retry_after}s"
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded. Maximum {info.limit} requests allowed "
                        f"per {self._format_window(endpoint, request)}. "
                        f"Please try again in {info.retry_after} seconds."
                    ),
                    "limit": info.limit,
                    "retry_after": info.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(info.limit),
                    "X-RateLimit-Remaining": str(info.remaining),
                    "X-RateLimit-Reset": str(info.reset),
                    "Retry-After": str(info.retry_after)
                }
            )

        # Process request normally
        response = await call_next(request)

        # Add rate limit headers to successful responses
        if info:
            response.headers["X-RateLimit-Limit"] = str(info.limit)
            response.headers["X-RateLimit-Remaining"] = str(info.remaining)
            response.headers["X-RateLimit-Reset"] = str(info.reset)

        return response

    def _get_client_key(self, request: Request) -> str:
        """
        Extract unique client identifier from request

        Handles proxy scenarios by checking X-Forwarded-For header first.

        Args:
            request: HTTP request

        Returns:
            Client identifier string (format: "ip:session")
        """
        # Get IP address (handle proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in comma-separated list (original client)
            ip = forwarded_for.split(",")[0].strip()
        else:
            # Direct connection
            ip = request.client.host if request.client else "unknown"

        # Try to get session_id from request state (if set by endpoint)
        # For now, we'll use IP-only as session_id is in request body
        session_id = getattr(request.state, "session_id", None)

        # Create composite key
        session = session_id or "no_session"
        return f"{ip}:{session}"

    def _format_window(self, endpoint: str, request: Request) -> str:
        """
        Format the time window for display in error messages

        Args:
            endpoint: Endpoint path
            request: HTTP request

        Returns:
            Human-readable time window (e.g., "minute", "hour")
        """
        service = self._get_rate_limit_service(request)
        if not service:
            return "time window"

        config = service.get_endpoint_config(endpoint)
        if not config:
            return "time window"

        # Format based on window size
        if config.window_seconds == 60:
            return "minute"
        elif config.window_seconds == 3600:
            return "hour"
        elif config.window_seconds < 60:
            return f"{config.window_seconds} seconds"
        elif config.window_seconds % 3600 == 0:
            hours = config.window_seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif config.window_seconds % 60 == 0:
            minutes = config.window_seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return f"{config.window_seconds} seconds"
