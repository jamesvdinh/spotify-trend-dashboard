"""Structured Streaming job: Kafka -> parse/flatten -> dedupe -> BigQuery raw table.

Landed already flattened (typed columns, not a JSON blob) - a deliberate
one-off deviation from the ingestion-scripts' raw-JSON convention, since
Spark already has to parse into a StructType for the watermark/dedup and
re-serializing to a blob just to re-parse it in dbt would add nothing.

Run via: python spark/streaming_job.py (see spark/Dockerfile - this runs as
a plain pip-installed pyspark script, not spark-submit, since it doesn't
depend on any prebuilt Spark distribution image).
"""
import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

SPARK_PACKAGES = (
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
    "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1"
)
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = "spotify.now_playing.events"
BQ_PROJECT_ID = os.environ.get("BQ_PROJECT_ID", "spotify-trend-dashboard")
BQ_TABLE = f"{BQ_PROJECT_ID}.raw.spotify_now_playing_events"
CHECKPOINT_LOCATION = os.environ.get("CHECKPOINT_LOCATION", "/opt/spark-checkpoints/now_playing")

# Mirrors the JSON payload backend/streaming/now_playing_producer.py publishes.
EVENT_SCHEMA = StructType(
    [
        StructField("user_id", StringType()),
        StructField("track_id", StringType()),
        StructField("track_name", StringType()),
        StructField("artist_names", StringType()),
        StructField("album_image_url", StringType()),
        StructField("is_playing", BooleanType()),
        StructField("progress_ms", LongType()),
        StructField("duration_ms", LongType()),
        StructField("played_at", DoubleType()),  # unix seconds
        StructField("context_uri", StringType()),
        StructField("polled_at", DoubleType()),  # unix seconds
    ]
)


def build_events_df(spark: SparkSession) -> DataFrame:
    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = raw.select(
        F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("event")
    ).select("event.*")

    return (
        parsed.withColumn("played_at", F.col("played_at").cast("timestamp"))
        .withColumn("polled_at", F.col("polled_at").cast("timestamp"))
        .withColumn("loaded_at", F.current_timestamp())
        .withWatermark("played_at", "10 minutes")
        # Standard Structured Streaming bounded-state dedup: the watermark
        # column (played_at) must be part of the dropDuplicates subset so
        # Spark can expire old dedup state instead of holding it forever.
        .dropDuplicates(["user_id", "track_id", "played_at"])
    )


def write_batch_to_bigquery(batch_df: DataFrame, batch_id: int) -> None:
    if batch_df.isEmpty():
        return
    (
        batch_df.write.format("bigquery")
        .option("table", BQ_TABLE)
        .option("writeMethod", "direct")
        .mode("append")
        .save()
    )


def main() -> None:
    spark = (
        SparkSession.builder.appName("spotify-now-playing-streaming")
        .config("spark.jars.packages", SPARK_PACKAGES)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    events = build_events_df(spark)

    query = (
        events.writeStream.foreachBatch(write_batch_to_bigquery)
        .option("checkpointLocation", CHECKPOINT_LOCATION)
        .trigger(processingTime="30 seconds")
        .start()
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()
