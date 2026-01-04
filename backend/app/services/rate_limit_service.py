"""Rate limiting service with sliding window algorithm"""

import time
import logging
import asyncio
from collections import deque, defaultdict
from typing import Dict, Optional, Tuple

from ..models.rate_limit import RateLimitConfig, RateLimitInfo

logger = logging.getLogger(__name__)


class RateLimitService:
    """
    Rate limiting service using sliding window counter algorithm

    Tracks requests per client (identified by IP:session) and enforces
    configurable rate limits per endpoint.
    """

    def __init__(self):
        # Structure: {"ip:session": {"requests": deque([ts1, ts2, ...]), "first_request": ts, "last_request": ts}}
        self._store: Dict[str, Dict] = defaultdict(self._new_bucket)
        self._lock = asyncio.Lock()
        self._configs: Dict[str, RateLimitConfig] = {}
        logger.info("RateLimitService initialized")

    def _new_bucket(self) -> Dict:
        """Create a new rate limit bucket for a client"""
        return {
            "requests": deque(),
            "first_request": None,
            "last_request": None
        }

    def register_endpoint(self, path: str, config: RateLimitConfig):
        """
        Register rate limit configuration for an endpoint

        Args:
            path: Endpoint path (e.g., "/api/chat/message")
            config: Rate limit configuration
        """
        self._configs[path] = config
        logger.info(
            f"Registered rate limit for {path}: "
            f"{config.requests} requests per {config.window_seconds}s "
            f"({config.requests_per_minute:.1f} req/min)"
        )

    async def check_rate_limit(
        self,
        client_key: str,
        endpoint: str
    ) -> Tuple[bool, Optional[RateLimitInfo]]:
        """
        Check if a request should be allowed based on rate limits

        Args:
            client_key: Unique identifier for the client (e.g., "ip:session")
            endpoint: Endpoint path being accessed

        Returns:
            Tuple of (allowed: bool, info: RateLimitInfo or None)
            - allowed: True if request should proceed, False if rate limited
            - info: Rate limit information for headers (None if no limit configured)
        """
        config = self._configs.get(endpoint)
        if not config:
            # No rate limit configured for this endpoint
            return True, None

        async with self._lock:
            current_time = time.time()
            bucket = self._store[client_key]

            # Cleanup: Remove timestamps outside the sliding window
            window_start = current_time - config.window_seconds
            while bucket["requests"] and bucket["requests"][0] < window_start:
                bucket["requests"].popleft()

            request_count = len(bucket["requests"])

            # Check if limit exceeded
            if request_count >= config.requests:
                # Calculate when the oldest request will expire
                oldest_request = bucket["requests"][0]
                retry_after = int(oldest_request + config.window_seconds - current_time) + 1

                info = RateLimitInfo(
                    limit=config.requests,
                    remaining=0,
                    reset=int(oldest_request + config.window_seconds),
                    retry_after=retry_after
                )

                logger.debug(
                    f"Rate limit exceeded for {client_key} on {endpoint}: "
                    f"{request_count}/{config.requests} requests"
                )

                return False, info

            # Allow request - add timestamp to bucket
            bucket["requests"].append(current_time)
            if not bucket["first_request"]:
                bucket["first_request"] = current_time
            bucket["last_request"] = current_time

            info = RateLimitInfo(
                limit=config.requests,
                remaining=config.requests - request_count - 1,
                reset=int(current_time + config.window_seconds)
            )

            logger.debug(
                f"Rate limit check passed for {client_key} on {endpoint}: "
                f"{request_count + 1}/{config.requests} requests, "
                f"{info.remaining} remaining"
            )

            return True, info

    async def cleanup_stale_buckets(self, max_age_seconds: int = 3600):
        """
        Remove buckets with no recent activity to prevent memory leaks

        Args:
            max_age_seconds: Maximum age in seconds for inactive buckets (default: 1 hour)
        """
        async with self._lock:
            current_time = time.time()
            stale_keys = [
                key for key, bucket in self._store.items()
                if bucket["last_request"]
                and (current_time - bucket["last_request"]) > max_age_seconds
            ]

            for key in stale_keys:
                del self._store[key]

            if stale_keys:
                logger.info(f"Cleaned up {len(stale_keys)} stale rate limit buckets")
            else:
                logger.debug("Rate limit cleanup: no stale buckets found")

    def get_endpoint_config(self, endpoint: str) -> Optional[RateLimitConfig]:
        """
        Get rate limit configuration for a specific endpoint

        Args:
            endpoint: Endpoint path

        Returns:
            RateLimitConfig if configured, None otherwise
        """
        return self._configs.get(endpoint)

    def get_stats(self) -> Dict:
        """
        Get current statistics about rate limiting

        Returns:
            Dictionary with statistics
        """
        return {
            "active_buckets": len(self._store),
            "configured_endpoints": len(self._configs),
            "endpoints": {
                path: {
                    "requests": config.requests,
                    "window_seconds": config.window_seconds,
                    "requests_per_minute": config.requests_per_minute
                }
                for path, config in self._configs.items()
            }
        }
