"""Middleware package for Chat Magic"""

from .rate_limit import RateLimitMiddleware

__all__ = ["RateLimitMiddleware"]
