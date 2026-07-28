"""Redis-backed session store.

Backed by Redis (not an in-process dict) because sessions must be visible
outside the request/response cycle: the streaming poller (backend/streaming/)
runs as its own process and needs to read/refresh the same access tokens.
"""
import json
import time
import uuid
from typing import Any, Optional, TypedDict

import redis

from .config import get_settings

SESSION_KEY_PREFIX = "session:"
ACTIVE_SESSIONS_KEY = "sessions:active"
NOW_PLAYING_KEY_PREFIX = "nowplaying:"
NOW_PLAYING_TTL_SECONDS = 60
PRODUCER_HEALTH_KEY = "health:producer:last_tick"


class TokenBundle(TypedDict):
    access_token: str
    refresh_token: str
    expires_at: float  # unix timestamp
    user_id: str


_redis: redis.Redis = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)


def _session_key(session_id: str) -> str:
    return f"{SESSION_KEY_PREFIX}{session_id}"


def create_session(tokens: TokenBundle) -> str:
    session_id = uuid.uuid4().hex
    _redis.hset(_session_key(session_id), mapping=dict(tokens))
    return session_id


def get_session(session_id: str) -> Optional[TokenBundle]:
    raw = _redis.hgetall(_session_key(session_id))
    if not raw:
        return None
    return {
        "access_token": raw["access_token"],
        "refresh_token": raw["refresh_token"],
        "expires_at": float(raw["expires_at"]),
        "user_id": raw["user_id"],
    }


def update_session(session_id: str, tokens: TokenBundle) -> None:
    _redis.hset(_session_key(session_id), mapping=dict(tokens))


def delete_session(session_id: str) -> None:
    _redis.delete(_session_key(session_id))
    _redis.zrem(ACTIVE_SESSIONS_KEY, session_id)


def is_expired(tokens: TokenBundle) -> bool:
    return time.time() >= tokens["expires_at"]


def touch_last_seen(session_id: str) -> None:
    """Record that a session is actively in use. Called by the heartbeat
    endpoint; the streaming poller reads ACTIVE_SESSIONS_KEY to find users
    currently in the app.
    """
    _redis.zadd(ACTIVE_SESSIONS_KEY, {session_id: time.time()})


def active_session_ids(within_seconds: float) -> list[str]:
    """Session ids that sent a heartbeat within the last `within_seconds`."""
    cutoff = time.time() - within_seconds
    return _redis.zrangebyscore(ACTIVE_SESSIONS_KEY, cutoff, "+inf")


def _now_playing_key(user_id: str) -> str:
    return f"{NOW_PLAYING_KEY_PREFIX}{user_id}"


def get_now_playing(user_id: str) -> Optional[dict[str, Any]]:
    """The hot-path cache the /api/now-playing endpoint reads from."""
    raw = _redis.get(_now_playing_key(user_id))
    return json.loads(raw) if raw else None


def set_now_playing(user_id: str, event: dict[str, Any]) -> None:
    """Written by the streaming poller on every real change (track/playing-state
    flip). TTL'd so a dead poller or closed tab self-heals to "nothing playing"
    instead of showing a frozen stale state forever.
    """
    _redis.set(_now_playing_key(user_id), json.dumps(event), ex=NOW_PLAYING_TTL_SECONDS)


def record_producer_heartbeat() -> None:
    """Written by the streaming poller each loop; read by an Airflow health
    check to detect a dead/stuck poller.
    """
    _redis.set(PRODUCER_HEALTH_KEY, time.time())
