"""Celery app configuration.

This project uses Redis as broker and result backend.
Do not put business logic here; tasks call engines/repositories.
"""

from __future__ import annotations

from celery import Celery  # pyright: ignore[reportMissingTypeStubs]

from ..core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lms",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Task modules
celery_app.autodiscover_tasks([
    "lms.app.workers.tasks",
])
