"""
Structured logging configuration with correlation IDs.

Features:
- JSON formatted logs for machine readability
- Correlation IDs (request_id, user_id)
- No PII or secrets logged
"""

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

# Context variables for propagating correlation IDs through async code
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)


class StructuredJSONFormatter(logging.Formatter):
    """
    Structured JSON logging formatter.

    Outputs logs as JSON with correlation context baked in.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation IDs if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = {
                "type": (
                    record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
                ),
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
            }

        # Add extra fields passed via logger.info(..., extra={...})
        extra = getattr(record, "extra_fields", None)
        if extra and isinstance(extra, dict):
            log_data.update(extra)

        return json.dumps(log_data)


def configure_logging(debug: bool = False) -> None:
    """
    Configure application-wide logging with JSON output.

    Args:
        debug: Enable DEBUG level logging if True
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)

    formatter = StructuredJSONFormatter()
    handler.setFormatter(formatter)

    # Clear existing handlers and add ours
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Suppress overly verbose third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def log_context(request_id: str | None = None, user_id: str | None = None) -> None:
    """
    Set correlation context for current task/request.

    Args:
        request_id: Unique request identifier
        user_id: Authenticated user ID (if available)
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)


def get_request_id() -> str | None:
    """Get current request ID from context."""
    return request_id_var.get()


def get_user_id() -> str | None:
    """Get current user ID from context."""
    return user_id_var.get()
