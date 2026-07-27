"""Load helper for ingestion scripts. get_client() lives in app.bigquery_client
(shared with the FastAPI serving layer) and is re-exported here so existing
`bq.get_client()` calls in the ingestion scripts keep working unchanged.
"""
from google.cloud import bigquery

from app.bigquery_client import get_client

__all__ = ["get_client", "load_rows"]


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
