"""
Metrics endpoint - exposes system metrics in Prometheus format.

GET /metrics - Returns Prometheus-compatible metrics
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from lms.app.metrics import render_metrics

router = APIRouter(tags=["observability"])


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics() -> str:
    """
    Return metrics in Prometheus text format.

    This endpoint is read-only and does not require authentication.

    Returns:
        Prometheus-formatted metrics (text/plain)
    """
    return render_metrics()
