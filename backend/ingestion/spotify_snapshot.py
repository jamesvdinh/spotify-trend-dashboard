"""Loads a daily personal-taste snapshot (top tracks + top artists) into BigQuery.

Requires SPOTIFY_REFRESH_TOKEN in backend/.env (see get_refresh_token.py).
Run daily via cron: python -m ingestion.spotify_snapshot
"""
import asyncio
from datetime import datetime, timezone
from typing import Any

from app.config import Settings, get_settings
from app.spotify_client import (
    get_current_user_profile,
    get_top_artists,
    get_top_tracks,
    refresh_access_token,
    tokens_to_bundle,
)
from ingestion import bq

TIME_RANGES = ["short_term", "medium_term", "long_term"]

TRACKS_TABLE = "raw.spotify_top_tracks_snapshot"
ARTISTS_TABLE = "raw.spotify_top_artists_snapshot"


async def _get_access_token(settings: Settings) -> str:
    if not settings.spotify_refresh_token:
        raise SystemExit(
            "SPOTIFY_REFRESH_TOKEN is not set. Run `python -m ingestion.get_refresh_token` first."
        )
    token_response = await refresh_access_token(settings, settings.spotify_refresh_token)
    tokens = tokens_to_bundle(token_response, previous_refresh_token=settings.spotify_refresh_token)
    return tokens["access_token"]


def _snapshot_rows(
    user_id: str,
    snapshot_date: str,
    time_range: str,
    items: list[dict[str, Any]],
    id_field: str,
    json_field: str,
    loaded_at: str,
) -> list[dict[str, Any]]:
    return [
        {
            "user_id": user_id,
            "snapshot_date": snapshot_date,
            "time_range": time_range,
            "rank": rank,
            id_field: item.get("id"),
            json_field: item,
            "loaded_at": loaded_at,
        }
        for rank, item in enumerate(items, start=1)
    ]


async def main() -> None:
    settings = get_settings()
    access_token = await _get_access_token(settings)
    profile = await get_current_user_profile(access_token)
    user_id = profile["id"]

    snapshot_date = datetime.now(timezone.utc).date().isoformat()
    loaded_at = datetime.now(timezone.utc).isoformat()

    track_rows: list[dict[str, Any]] = []
    artist_rows: list[dict[str, Any]] = []

    for time_range in TIME_RANGES:
        tracks_json, artists_json = await asyncio.gather(
            get_top_tracks(access_token, time_range=time_range, limit=50),
            get_top_artists(access_token, time_range=time_range, limit=50),
        )
        track_rows += _snapshot_rows(
            user_id, snapshot_date, time_range, tracks_json.get("items", []),
            "track_id", "track_json", loaded_at,
        )
        artist_rows += _snapshot_rows(
            user_id, snapshot_date, time_range, artists_json.get("items", []),
            "artist_id", "artist_json", loaded_at,
        )

    client = bq.get_client()
    bq.load_rows(client, f"{settings.bq_project_id}.{TRACKS_TABLE}", track_rows)
    bq.load_rows(client, f"{settings.bq_project_id}.{ARTISTS_TABLE}", artist_rows)

    print(f"Loaded {len(track_rows)} track rows and {len(artist_rows)} artist rows "
          f"for user {user_id} on {snapshot_date}")


if __name__ == "__main__":
    asyncio.run(main())
