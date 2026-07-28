from fastapi import Cookie, Depends, HTTPException, status

from . import session_store
from .config import Settings, get_settings
from .spotify_client import refresh_access_token, tokens_to_bundle


async def get_access_token(
    session_id: str | None = Cookie(default=None, alias="session_id"),
    settings: Settings = Depends(get_settings),
) -> str:
    if session_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")

    tokens = session_store.get_session(session_id)
    if tokens is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired or unknown")

    if session_store.is_expired(tokens):
        token_response = await refresh_access_token(settings, tokens["refresh_token"])
        refreshed = tokens_to_bundle(token_response, previous_refresh_token=tokens["refresh_token"])
        tokens = {**tokens, **refreshed}
        session_store.update_session(session_id, tokens)

    return tokens["access_token"]
