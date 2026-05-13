"""
Core dependency injection for FastAPI routes.
"""

from __future__ import annotations

from backend.storage.local import local_storage
from backend.ingestion.pipeline import ingestion_pipeline
from backend.utils.token_metrics import token_metrics


def get_storage() -> type(local_storage):
    """DI: Get storage backend."""
    return local_storage


def get_pipeline() -> type(ingestion_pipeline):
    """DI: Get ingestion pipeline."""
    return ingestion_pipeline


def get_token_metrics() -> type(token_metrics):
    """DI: Get token metrics tracker."""
    return token_metrics