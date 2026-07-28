"""Daily batch ingestion - replaces .github/workflows/ingest.yml.

Runs the same two ingestion scripts GH Actions used to run
(backend/ingestion/spotify_snapshot.py, backend/ingestion/kworb_scraper.py),
then a dbt build over the whole project. BashOperator rather than
PythonOperator: these scripts are already self-contained `python -m
ingestion.X` CLI processes with their own asyncio.run() entrypoint, so
shelling out (matching how GH Actions already invoked them) avoids sharing
an event loop/interpreter state with the Airflow worker process.
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

BACKEND_DIR = "/opt/airflow/project/backend"
DBT_PROJECT_DIR = "/opt/airflow/project/dbt"
DBT_PROFILES_DIR = "/opt/airflow/dbt_profiles"

with DAG(
    dag_id="daily_batch_ingestion",
    description="Spotify + Kworb daily snapshots -> BigQuery raw -> dbt build",
    schedule="0 13 * * *",  # matches ingest.yml's existing daily 13:00 UTC cron
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ingestion", "batch"],
) as dag:
    spotify_snapshot = BashOperator(
        task_id="spotify_snapshot",
        bash_command=f"cd {BACKEND_DIR} && python -m ingestion.spotify_snapshot",
    )

    kworb_scrape = BashOperator(
        task_id="kworb_scrape",
        bash_command=f"cd {BACKEND_DIR} && python -m ingestion.kworb_scraper",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"dbt build --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
    )

    [spotify_snapshot, kworb_scrape] >> dbt_build
