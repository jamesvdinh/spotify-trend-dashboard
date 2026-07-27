"""Scrapes Kworb's global artist streams leaderboard into BigQuery.

Kworb (kworb.net) has no API -- this parses the HTML table directly. If Kworb
ever changes the table layout, this raises instead of silently loading
garbage. Run daily via cron: python -m ingestion.kworb_scraper
"""
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from ingestion import bq

URL = "https://kworb.net/spotify/artists.html"
TABLE = "raw.kworb_artist_streams_snapshot"

EXPECTED_HEADERS = ["Artist", "Streams", "Daily", "As lead", "Solo", "As feature"]
_ARTIST_ID_RE = re.compile(r"/spotify/artist/([^_/]+)_songs\.html")


def _parse_number(text: str) -> float | None:
    text = text.strip().replace(",", "")
    return float(text) if text else None


def fetch_html() -> str:
    response = httpx.get(
        URL,
        headers={"User-Agent": "spotify-trend-dashboard/1.0 (personal project; single daily scrape)"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def parse_rows(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("Kworb page layout changed: no <table> found")

    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    if headers != EXPECTED_HEADERS:
        raise RuntimeError(f"Kworb table headers changed: expected {EXPECTED_HEADERS}, got {headers}")

    rows = []
    for rank, tr in enumerate(table.find("tbody").find_all("tr"), start=1):
        cells = tr.find_all("td")
        if len(cells) != len(EXPECTED_HEADERS):
            raise RuntimeError(f"Kworb row has {len(cells)} cells, expected {len(EXPECTED_HEADERS)}")

        link = cells[0].find("a")
        if link is None:
            raise RuntimeError("Kworb row missing artist link")
        match = _ARTIST_ID_RE.search(link["href"])
        if not match:
            raise RuntimeError(f"Could not parse artist id from href: {link['href']}")

        rows.append({
            "rank": rank,
            "artist_id": match.group(1),
            "artist_name": link.get_text(strip=True),
            "total_streams_millions": _parse_number(cells[1].get_text()),
            "daily_streams_millions": _parse_number(cells[2].get_text()),
            "streams_lead_millions": _parse_number(cells[3].get_text()),
            "streams_solo_millions": _parse_number(cells[4].get_text()),
            "streams_featured_millions": _parse_number(cells[5].get_text()),
        })
    return rows


def main() -> None:
    settings = get_settings()
    parsed = parse_rows(fetch_html())

    snapshot_date = datetime.now(timezone.utc).date().isoformat()
    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [{**row, "snapshot_date": snapshot_date, "loaded_at": loaded_at} for row in parsed]

    client = bq.get_client()
    bq.load_rows(client, f"{settings.bq_project_id}.{TABLE}", rows)
    print(f"Loaded {len(rows)} artist chart rows for {snapshot_date}")


if __name__ == "__main__":
    main()
