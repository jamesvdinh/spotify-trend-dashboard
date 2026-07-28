import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from .. import session_store
from ..config import Settings, get_settings
from ..spotify_client import (
    build_authorize_url,
    exchange_code_for_tokens,
    get_current_user_profile,
    tokens_to_bundle,
)

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE_NAME = "spotify_auth_state"


@router.get("/login")
def login(response: Response, settings: Settings = Depends(get_settings)):
    state = secrets.token_urlsafe(16)
    response = RedirectResponse(build_authorize_url(settings, state))
    response.set_cookie(
        STATE_COOKIE_NAME,
        state,
        httponly=True,
        max_age=600,
        samesite="lax",
    )
    return response


@router.get("/callback")
async def callback(
    response: Response,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    spotify_auth_state: str | None = Cookie(default=None, alias=STATE_COOKIE_NAME),
    settings: Settings = Depends(get_settings),
):
    if error is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Spotify auth error: {error}")

    if code is None or state is None or state != spotify_auth_state:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or missing OAuth state")

    token_response = await exchange_code_for_tokens(settings, code)
    tokens = tokens_to_bundle(token_response)
    profile = await get_current_user_profile(tokens["access_token"])
    tokens["user_id"] = profile["id"]
    session_id = session_store.create_session(tokens)

    redirect = RedirectResponse(f"{settings.frontend_url}/dashboard")
    redirect.delete_cookie(STATE_COOKIE_NAME)
    redirect.set_cookie(
        settings.session_cookie_name,
        session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return redirect


@router.post("/logout")
def logout(
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    settings: Settings = Depends(get_settings),
):
    if session_id is not None:
        session_store.delete_session(session_id)
    response.delete_cookie(settings.session_cookie_name)
    return {"ok": True}
