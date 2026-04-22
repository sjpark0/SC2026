from __future__ import annotations

from celery import Celery

from .config import get_settings

settings = get_settings()

app = Celery(
    "npo-cli-pipeline",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["npo_cli_pipeline.tasks"],
)
