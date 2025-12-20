"""
API request timing and metrics collection middleware.

Records request duration and status for metrics.
"""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..metrics import api_request_duration_seconds, api_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Collect metrics on API requests.

    Records:
    - Request duration
    - Request count by route/method/status
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Record metrics for this request."""
        start_time = time.time()

        # Get path (normalize for metrics)
        path = request.url.path
        # Replace UUID path params with placeholder
        parts = path.split("/")
        normalized_parts = []
        for part in parts:
            # Simple heuristic: UUIDs are 36 chars
            if len(part) == 36 and part.count("-") == 4:
                normalized_parts.append(":id")
            else:
                normalized_parts.append(part)
        route = "/".join(normalized_parts)

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        status_code = response.status_code

        # Counter: requests by route/method/status
        api_requests_total.inc((route, request.method, status_code))

        # Histogram: request duration
        api_request_duration_seconds.observe(duration)

        return response
