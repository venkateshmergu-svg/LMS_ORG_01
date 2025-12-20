"""
Request context middleware - propagates correlation IDs through requests.

Generates unique request_id for each API request and propagates it through
logs, audit events, and domain events for full traceability.
"""

import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..core.logging import log_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches correlation IDs to each request.

    - Generates request_id if not provided
    - Attaches user_id if authenticated
    - Propagates through logging context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and propagate correlation context.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with correlation context propagated
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Extract user ID from JWT if authenticated
        # The auth dependency in deps.py will have set it if valid
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = str(request.state.user_id)

        # Set correlation context for this request
        log_context(request_id=request_id, user_id=user_id)

        # Attach to request state for access in handlers
        request.state.request_id = request_id
        request.state.user_id = user_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers for client correlation
        response.headers["X-Request-ID"] = request_id

        return response
