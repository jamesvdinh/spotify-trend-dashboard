"""Thin wrapper around the Spotify Accounts + Web API endpoints used for OAuth."""
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from .config import Settings

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
ME_URL = "https://api.spotify.com/v1/me"
TOP_TRACKS_URL = "https://api.spotify.com/v1/me/top/tracks"
TOP_ARTISTS_URL = "https://api.spotify.com/v1/me/top/artists"

SCOPES = "user-read-private user-read-email user-top-read"


def build_authorize_url(settings: Settings, state: str) -> str:
    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "state": state,
        "scope": SCOPES,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(settings: Settings, code: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.spotify_redirect_uri,
            },
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
        response.raise_for_status()
        return response.json()


async def refresh_access_token(settings: Settings, refresh_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
        response.raise_for_status()
        return response.json()


def tokens_to_bundle(token_response: dict[str, Any], previous_refresh_token: str | None = None) -> dict[str, Any]:
    return {
        "access_token": token_response["access_token"],
        # Spotify only returns a new refresh_token sometimes; keep the old one otherwise.
        "refresh_token": token_response.get("refresh_token", previous_refresh_token),
        "expires_at": time.time() + token_response["expires_in"],
    }


async def get_current_user_profile(access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


async def get_top_tracks(access_token: str, time_range: str = "long_term", limit: int = 50) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            TOP_TRACKS_URL,
            params={"time_range": time_range, "limit": limit},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


async def get_top_artists(access_token: str, time_range: str = "long_term", limit: int = 50) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            TOP_ARTISTS_URL,
            params={"time_range": time_range, "limit": limit},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
