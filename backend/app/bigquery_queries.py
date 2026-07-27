"""Read-side BigQuery queries backing the FastAPI serving layer."""
from typing import Any

from google.cloud import bigquery

from .bigquery_client import get_client
from .config import get_settings


def query_personal_vs_global(user_id: str) -> list[dict[str, Any]]:
    settings = get_settings()
    client = get_client()
    table = f"{settings.bq_project_id}.marts.fct_personal_vs_global"

    query = f"""
        SELECT
            time_range,
            snapshot_date,
            artist_id,
            artist_name,
            personal_rank,
            global_rank,
            global_rank_change_7d,
            global_daily_streams_millions
        FROM `{table}`
        WHERE user_id = @user_id
          AND snapshot_date = (SELECT MAX(snapshot_date) FROM `{table}` WHERE user_id = @user_id)
        ORDER BY time_range, personal_rank
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]
