import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from .. import bigquery_queries, session_store, taste_metrics
from ..deps import get_access_token, require_session
from ..spotify_client import get_current_user_profile, get_top_artists, get_top_tracks

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/me")
async def me(access_token: str = Depends(get_access_token)):
    profile = await get_current_user_profile(access_token)
    return {
        "id": profile.get("id"),
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "product": profile.get("product"),
        "followers": profile.get("followers", {}).get("total"),
        "images": profile.get("images", []),
        "external_url": profile.get("external_urls", {}).get("spotify"),
        "country": profile.get("country"),
    }


@router.get("/taste")
async def taste(access_token: str = Depends(get_access_token)):
    try:
        tracks_json, artists_json = await asyncio.gather(
            get_top_tracks(access_token, limit=50),
            get_top_artists(access_token, limit=50),
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 403:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                {
                    "error": "insufficient_scope",
                    "message": "Reconnect your Spotify account to see your top tracks and listening taste.",
                },
            ) from exc
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Spotify API error") from exc

    tracks = tracks_json.get("items", [])
    artists = artists_json.get("items", [])
    return {
        "top_tracks": taste_metrics.format_top_tracks(tracks, limit=5),
        "metrics": taste_metrics.build_metrics(tracks, artists),
    }


@router.get("/trends")
async def trends(access_token: str = Depends(get_access_token)):
    profile = await get_current_user_profile(access_token)
    user_id = profile.get("id")
    rows = await asyncio.to_thread(bigquery_queries.query_personal_vs_global, user_id)
    return {"personal_vs_global": rows}


@router.post("/heartbeat")
async def heartbeat(session_id: str = Depends(require_session)):
    """Called periodically by the frontend while the dashboard is open, so the
    streaming poller (backend/streaming/) knows which users are actively in
    the app right now.
    """
    session_store.touch_last_seen(session_id)
    return {"ok": True}


@router.get("/now-playing")
async def now_playing(session_id: str = Depends(require_session)):
    """Reads the streaming poller's hot-path Redis cache directly - no
    Spotify call here, so this stays cheap enough for the frontend to poll
    every few seconds.
    """
    tokens = session_store.get_session(session_id)
    if tokens is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired or unknown")

    event = session_store.get_now_playing(tokens["user_id"])
    if event is None:
        return {"is_playing": False}
    return event
