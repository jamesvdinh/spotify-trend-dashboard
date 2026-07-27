"""Shared BigQuery client + load helper for ingestion scripts."""
import os

from google.cloud import bigquery

from app.config import get_settings


def get_client() -> bigquery.Client:
    settings = get_settings()
    if settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
        )
    return bigquery.Client(project=settings.bq_project_id)


def load_rows(client: bigquery.Client, table: str, rows: list[dict]) -> None:
    """Batch-append rows into a raw.* table via a load job (not streaming inserts)."""
    if not rows:
        return

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    job = client.load_table_from_json(rows, table, job_config=job_config)
    job.result()  # raises if the load job failed (e.g. schema mismatch)
