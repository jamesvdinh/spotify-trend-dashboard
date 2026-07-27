"""Shared BigQuery client, used by both the FastAPI app and the ingestion scripts."""
import os

from google.cloud import bigquery

from .config import get_settings


def get_client() -> bigquery.Client:
    settings = get_settings()
    if settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
        )
    return bigquery.Client(project=settings.bq_project_id)
