"""One-off CLI to mint a Spotify refresh token for the ingestion scripts.

The web app only keeps refresh tokens in an in-memory session tied to a
browser cookie, so standalone scripts have no way to reuse it. Run this once
to get a durable token to store in backend/.env as SPOTIFY_REFRESH_TOKEN.

IMPORTANT: stop `uvicorn app.main:app` before running this — it binds
127.0.0.1:8000 itself to catch the same /auth/callback redirect URI
registered with Spotify.

Usage: python -m ingestion.get_refresh_token
"""
import asyncio
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from app.config import get_settings
from app.spotify_client import build_authorize_url, exchange_code_for_tokens

_result: dict[str, str] = {}


class _CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass  # silence default request logging

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        _result["code"] = params.get("code", [""])[0]
        _result["state"] = params.get("state", [""])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Done - you can close this tab and return to the terminal.")


async def main() -> None:
    settings = get_settings()
    state = secrets.token_urlsafe(16)
    auth_url = build_authorize_url(settings, state)

    print(f"Opening browser for Spotify login:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("127.0.0.1", 8000), _CallbackHandler)
    server.handle_request()  # blocks until the single redirect arrives

    if _result.get("state") != state:
        raise SystemExit("OAuth state mismatch - aborting.")
    if not _result.get("code"):
        raise SystemExit(f"No authorization code received: {_result}")

    tokens = await exchange_code_for_tokens(settings, _result["code"])
    print("\nAdd this to backend/.env:\n")
    print(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}")


if __name__ == "__main__":
    asyncio.run(main())
