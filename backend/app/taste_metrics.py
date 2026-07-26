"""Pure aggregation logic over Spotify top-tracks/top-artists payloads.

Kept framework-free (no fastapi/httpx imports) so it's checkable with plain
dict fixtures instead of a running server.
"""
from collections import Counter
from statistics import fmean
from typing import Any


def top_genre(artists: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not artists:
        return None

    counts = Counter(genre for artist in artists for genre in artist.get("genres", []))
    if not counts:
        return None

    name, count = counts.most_common(1)[0]
    return {"name": name, "share": round(count / len(artists) * 100, 1)}


def top_artist(artists: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not artists:
        return None

    artist = artists[0]
    images = artist.get("images") or []
    return {
        "name": artist.get("name"),
        "image": images[0]["url"] if images else None,
        "external_url": artist.get("external_urls", {}).get("spotify"),
    }


def avg_popularity(tracks: list[dict[str, Any]]) -> float | None:
    if not tracks:
        return None
    return round(fmean(t.get("popularity", 0) for t in tracks), 1)


def unique_artist_count(tracks: list[dict[str, Any]]) -> int:
    ids = {artist["id"] for track in tracks for artist in track.get("artists", []) if artist.get("id")}
    return len(ids)


def format_top_tracks(items: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    formatted = []
    for track in items[:limit]:
        images = track.get("album", {}).get("images") or []
        formatted.append({
            "id": track.get("id"),
            "name": track.get("name"),
            "artists": ", ".join(a["name"] for a in track.get("artists", [])),
            "album_image": images[0]["url"] if images else None,
            "external_url": track.get("external_urls", {}).get("spotify"),
            "duration_ms": track.get("duration_ms"),
            "popularity": track.get("popularity"),
        })
    return formatted


def build_metrics(tracks: list[dict[str, Any]], artists: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "top_genre": top_genre(artists),
        "top_artist": top_artist(artists),
        "avg_popularity": avg_popularity(tracks),
        "unique_artist_count": unique_artist_count(tracks),
    }
