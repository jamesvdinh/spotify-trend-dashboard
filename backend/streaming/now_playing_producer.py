"""Standalone process: polls Spotify's currently-playing endpoint for every
user actively in the app (tracked via session_store's heartbeat) and
publishes real changes to both a Redis hot cache (for the live "Now Playing"
widget) and a Kafka topic (the durable log the PySpark job consumes for
historical trend marts).

Run via: python -m streaming.now_playing_producer
"""
import asyncio
import json
import logging
import time
from typing import Any

from confluent_kafka import Producer

from app import session_store
from app.config import get_settings
from app.spotify_client import get_currently_playing, refresh_access_token, tokens_to_bundle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("now_playing_producer")

TOPIC = "spotify.now_playing.events"
POLL_INTERVAL_SECONDS = 5
ACTIVE_WINDOW_SECONDS = 30


def _extract_event(user_id: str, playback: dict[str, Any] | None) -> dict[str, Any]:
    polled_at = time.time()
    item = (playback or {}).get("item")

    if not item:
        return {
            "user_id": user_id,
            "track_id": None,
            "track_name": None,
            "artist_names": None,
            "album_image_url": None,
            "is_playing": False,
            "progress_ms": None,
            "duration_ms": None,
            "played_at": polled_at,
            "context_uri": None,
            "polled_at": polled_at,
        }

    images = item.get("album", {}).get("images") or []
    timestamp_ms = playback.get("timestamp")
    return {
        "user_id": user_id,
        "track_id": item.get("id"),
        "track_name": item.get("name"),
        "artist_names": ", ".join(a.get("name", "") for a in item.get("artists", [])),
        "album_image_url": images[0]["url"] if images else None,
        "is_playing": bool(playback.get("is_playing")),
        "progress_ms": playback.get("progress_ms"),
        "duration_ms": item.get("duration_ms"),
        "played_at": timestamp_ms / 1000 if timestamp_ms else polled_at,
        "context_uri": (playback.get("context") or {}).get("uri"),
        "polled_at": polled_at,
    }


def _changed(previous: dict[str, Any] | None, event: dict[str, Any]) -> bool:
    if previous is None:
        return True
    return (
        previous.get("track_id") != event["track_id"]
        or previous.get("is_playing") != event["is_playing"]
    )


class NowPlayingProducer:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._kafka = Producer({"bootstrap.servers": self._settings.kafka_bootstrap_servers})

    def _publish(self, event: dict[str, Any]) -> None:
        self._kafka.produce(
            TOPIC,
            key=event["user_id"].encode("utf-8"),
            value=json.dumps(event).encode("utf-8"),
        )
        self._kafka.poll(0)

    async def _poll_session(self, session_id: str) -> None:
        tokens = session_store.get_session(session_id)
        if tokens is None:
            return

        if session_store.is_expired(tokens):
            token_response = await refresh_access_token(self._settings, tokens["refresh_token"])
            refreshed = tokens_to_bundle(token_response, previous_refresh_token=tokens["refresh_token"])
            tokens = {**tokens, **refreshed}
            session_store.update_session(session_id, tokens)

        user_id = tokens["user_id"]
        playback = await get_currently_playing(tokens["access_token"])
        event = _extract_event(user_id, playback)

        # Seed comparison state from Redis rather than in-memory: on a
        # producer restart there is no in-memory "last known" state, and
        # without this it would re-publish a duplicate event for whatever
        # is already playing.
        previous = session_store.get_now_playing(user_id)
        if not _changed(previous, event):
            return

        session_store.set_now_playing(user_id, event)
        self._publish(event)
        logger.info(
            "now-playing changed: user=%s track=%s playing=%s",
            user_id, event["track_id"], event["is_playing"],
        )

    async def run_forever(self) -> None:
        logger.info("now-playing producer started, polling every %ss", POLL_INTERVAL_SECONDS)
        while True:
            session_ids = session_store.active_session_ids(ACTIVE_WINDOW_SECONDS)
            session_store.record_producer_heartbeat()

            results = await asyncio.gather(
                *(self._poll_session(sid) for sid in session_ids),
                return_exceptions=True,
            )
            for session_id, result in zip(session_ids, results):
                if isinstance(result, Exception):
                    logger.warning("poll failed for session %s: %s", session_id, result)

            self._kafka.flush(0)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)


def main() -> None:
    asyncio.run(NowPlayingProducer().run_forever())


if __name__ == "__main__":
    main()
