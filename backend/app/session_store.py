"""In-memory session store.

Boilerplate only: swap this for Redis (matching the project's cache layer)
once sessions need to survive a server restart or be shared across workers.
"""
import time
import uuid
from typing import Optional, TypedDict


class TokenBundle(TypedDict):
    access_token: str
    refresh_token: str
    expires_at: float  # unix timestamp


_SESSIONS: dict[str, TokenBundle] = {}


def create_session(tokens: TokenBundle) -> str:
    session_id = uuid.uuid4().hex
    _SESSIONS[session_id] = tokens
    return session_id


def get_session(session_id: str) -> Optional[TokenBundle]:
    return _SESSIONS.get(session_id)


def update_session(session_id: str, tokens: TokenBundle) -> None:
    _SESSIONS[session_id] = tokens


def delete_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)


def is_expired(tokens: TokenBundle) -> bool:
    return time.time() >= tokens["expires_at"]
