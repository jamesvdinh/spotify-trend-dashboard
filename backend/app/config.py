from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str = "http://127.0.0.1:8000/auth/callback"
    frontend_url: str = "http://127.0.0.1:5173"
    # Path under frontend_url where the app actually lives, e.g.
    # "/spotify-trend-dashboard" for a GitHub Pages project site. Kept
    # separate from frontend_url because CORS needs the bare origin (no
    # path), while the post-login redirect needs the full path - a GitHub
    # Pages project site is the case where those two differ.
    frontend_app_path: str = ""
    session_cookie_name: str = "session_id"
    redis_url: str = "redis://127.0.0.1:6379/0"
    kafka_bootstrap_servers: str = "127.0.0.1:9092"

    # Used by standalone ingestion scripts (backend/ingestion/), not the web app.
    spotify_refresh_token: str | None = None
    bq_project_id: str = "spotify-trend-dashboard"
    google_application_credentials: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
