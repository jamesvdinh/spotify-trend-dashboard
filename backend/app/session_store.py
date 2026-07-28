"""Redis-backed session store.

Backed by Redis (not an in-process dict) because sessions must be visible
outside the request/response cycle: the streaming poller (backend/streaming/)
runs as its own process and needs to read/refresh the same access tokens.
"""
import time
import uuid
from typing import Optional, TypedDict

import redis

from .config import get_settings

SESSION_KEY_PREFIX = "session:"
ACTIVE_SESSIONS_KEY = "sessions:active"


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
