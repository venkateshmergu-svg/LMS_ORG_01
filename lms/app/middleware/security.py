"""
Security hardening middleware and utilities.

Features:
- Rate limiting (basic per-IP)
- Security headers
- Error handling (no stack traces in responses)
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic per-IP rate limiting.

    Rules:
    - Write endpoints: 100 requests per 60 seconds per IP
    - Read endpoints: unlimited (or could add separate limit)
    """

    # IP -> list of (timestamp, endpoint) tuples
    request_log: dict = defaultdict(list)

    # Write endpoints that require rate limiting
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    # Rate limit: 100 requests per 60 seconds
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX = 100  # requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        # Only rate-limit write operations
        if request.method not in self.WRITE_METHODS:
            return await call_next(request)

        # Get client IP (accounting for proxies)
        client_ip = request.client.host if request.client else "unknown"

        # Get current time
        now = time.time()

        # Clean old requests (older than window)
        requests_in_window = [
            (ts, endpoint)
            for ts, endpoint in self.request_log.get(client_ip, [])
            if now - ts < self.RATE_LIMIT_WINDOW
        ]

        # Check limit
        if len(requests_in_window) >= self.RATE_LIMIT_MAX:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        # Record this request
        requests_in_window.append((now, request.url.path))
        self.request_log[client_ip] = requests_in_window

        # Proceed
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

    Never expose stack traces in production.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions gracefully."""
        try:
            return await call_next(request)
        except Exception:
            # Log the exception (will include correlation ID from logging context)
            import logging

            logger = logging.getLogger(__name__)
            logger.exception(
                f"Unhandled exception in {request.method} {request.url.path}"
            )

            # Return generic error (never expose internals)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error. Please try again later."},
            )
