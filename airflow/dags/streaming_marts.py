"""Periodic materialization of the streaming dbt marts, plus a health check
for the always-on Kafka producer.

The producer (backend/streaming/now_playing_producer.py) and the Spark
structured streaming job are long-running processes kept alive by
docker-compose's `restart: unless-stopped` - Airflow deliberately does not
try to run them *as* tasks, since a task that never finishes just blocks a
worker slot forever. Airflow's job here is only to (a) periodically
materialize the dbt marts on top of the raw rows Spark is continuously
landing, and (b) fail loudly if the producer's health-tick key goes stale,
which is as close as Airflow gets to supervising a process it doesn't run.
"""
import time
from datetime import datetime, timedelta

import redis
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT_PROJECT_DIR = "/opt/airflow/project/dbt"
DBT_PROFILES_DIR = "/opt/airflow/dbt_profiles"
REDIS_URL = "redis://redis:6379/0"
PRODUCER_HEALTH_KEY = "health:producer:last_tick"
# The producer ticks every ~5s (see POLL_INTERVAL_SECONDS in
# now_playing_producer.py); anything past a minute of silence means it's
# dead, not just between polls.
MAX_STALENESS_SECONDS = 60


def check_producer_health() -> None:
    client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    last_tick = client.get(PRODUCER_HEALTH_KEY)
    if last_tick is None:
        raise AirflowFailException("now_playing_producer has never reported a health tick")

    staleness = time.time() - float(last_tick)
    if staleness > MAX_STALENESS_SECONDS:
        raise AirflowFailException(
            f"now_playing_producer health tick is {staleness:.0f}s stale "
            f"(max {MAX_STALENESS_SECONDS}s) - the poller container may be dead"
        )


with DAG(
    dag_id="streaming_marts",
    description="Materialize streaming dbt marts + health-check the always-on producer",
    schedule=timedelta(minutes=15),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streaming", "dbt"],
) as dag:
    dbt_run_streaming_marts = BashOperator(
        task_id="dbt_run_streaming_marts",
        bash_command=(
            f"dbt run --select stg_spotify__now_playing+ "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    check_producer_health_task = PythonOperator(
        task_id="check_producer_health",
        python_callable=check_producer_health,
    )
