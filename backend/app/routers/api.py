import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from .. import taste_metrics
from ..deps import get_access_token
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
