"""
Security hardening middleware and utilities.

Features:
- Rate limiting (Redis-backed for distributed environments)
- Security headers
- Error handling (no stack traces in responses)
"""

import logging
import time
from collections import defaultdict
from typing import Callable, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiting with Redis support for distributed deployments.

    Rules:
    - Write endpoints: 100 requests per 60 seconds per IP
    - Read endpoints: unlimited (or could add separate limit)

    Architecture:
    - Uses Redis when available (production, multi-worker)
    - Falls back to in-memory (development, single-worker)
    """

    # Fallback in-memory storage (single-process only)
    _fallback_log: dict = defaultdict(list)
    _redis_client: Optional[object] = None
    _redis_checked: bool = False

    # Write endpoints that require rate limiting
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    @classmethod
    def reset(cls) -> None:
        """Reset rate limit counters. Useful for testing."""
        cls._fallback_log = defaultdict(list)

    # Rate limit: 100 requests per 60 seconds
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX = 100  # requests

    @classmethod
    def _get_redis_client(cls):
        """Lazy-load Redis client from app config."""
        if cls._redis_checked:
            return cls._redis_client

        cls._redis_checked = True
        try:
            import redis

            from ..core.config import get_settings

            settings = get_settings()
            cls._redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1,
            )
            # Test connection
            cls._redis_client.ping()
            logger.info("Rate limiter using Redis backend")
        except Exception as e:
            logger.warning(
                f"Redis unavailable for rate limiting, using in-memory fallback: {e}"
            )
            cls._redis_client = None

        return cls._redis_client

    def _check_rate_limit_redis(self, client_ip: str, now: float) -> bool:
        """Check rate limit using Redis. Returns True if exceeded."""
        redis_client = self._get_redis_client()
        if not redis_client:
            return self._check_rate_limit_memory(client_ip, now)

        try:
            key = f"ratelimit:{client_ip}"
            pipe = redis_client.pipeline()

            # Remove old entries and count recent ones
            window_start = now - self.RATE_LIMIT_WINDOW
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.RATE_LIMIT_WINDOW + 1)

            results = pipe.execute()
            count = results[1]

            return count >= self.RATE_LIMIT_MAX
        except Exception as e:
            logger.warning(f"Redis rate limit check failed, using fallback: {e}")
            return self._check_rate_limit_memory(client_ip, now)

    def _check_rate_limit_memory(self, client_ip: str, now: float) -> bool:
        """Check rate limit using in-memory storage. Returns True if exceeded."""
        # Clean old requests
        requests_in_window = [
            ts
            for ts in self._fallback_log.get(client_ip, [])
            if now - ts < self.RATE_LIMIT_WINDOW
        ]

        # Check limit
        if len(requests_in_window) >= self.RATE_LIMIT_MAX:
            return True

        # Record this request
        requests_in_window.append(now)
        self._fallback_log[client_ip] = requests_in_window
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        # Only rate-limit write operations
        if request.method not in self.WRITE_METHODS:
            return await call_next(request)

        # Get client IP (accounting for proxies)
        # Check X-Forwarded-For for load balancer/proxy setups
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        now = time.time()

        # Check rate limit
        if self._check_rate_limit_redis(client_ip, now):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(self.RATE_LIMIT_WINDOW)},
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # No sniff
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catch unhandled exceptions and return safe error responses.

    Converts domain exceptions to proper HTTP responses.
    Never expose stack traces in production.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions gracefully."""
        try:
            return await call_next(request)
        except Exception as exc:
            import logging

            from ..core.exceptions import (
                EntityNotFoundException,
                LeaveException,
                LMSException,
                PolicyException,
                WorkflowStateException,
            )

            logger = logging.getLogger(__name__)

            # Map domain exceptions to HTTP status codes
            if isinstance(exc, EntityNotFoundException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": str(exc)},
                )
            elif isinstance(exc, WorkflowStateException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": str(exc)},
                )
            elif isinstance(exc, (LeaveException, PolicyException)):
                # LeaveOverlapException, InsufficientBalanceException, PolicyValidationException, etc.
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": str(exc),
                        "errors": getattr(exc, "details", None),
                    },
                )
            elif isinstance(exc, LMSException):
                # Other domain exceptions
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": str(exc)},
                )

            # Log truly unexpected exceptions
            logger.exception(
                f"Unhandled exception in {request.method} {request.url.path}"
            )

            # Return generic error (never expose internals)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error. Please try again later."},
            )
