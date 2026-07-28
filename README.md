# Spotify Trend Dashboard

An end-to-end system that ingests Spotify listening and chart data, computes
trend signals (rising-artist velocity, chart lag, etc.), and lets users
compare their own listening habits against global trends.

A FastAPI backend handles the Spotify login flow and serves dbt-modeled
BigQuery marts; a React dashboard shows the logged-in user's profile, taste,
trends, and a live "now playing" widget. Batch ingestion (daily Spotify +
Kworb snapshots) and a real-time layer (Kafka + PySpark + Redis for a live
now-playing feed) both feed BigQuery, with Airflow orchestrating both the
daily batch DAG and the streaming marts. See `docker-compose.yml` for the
full local stack and `deploy/README.md` for running it on a real VPS.

## Prerequisites

Create a Spotify app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and add
`http://127.0.0.1:8000/auth/callback` as a Redirect URI.

## Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET
uvicorn app.main:app --reload
```

Runs on [127.0.0.1:8000](http://127.0.0.1:8000). Routes:

- `GET /auth/login` — redirects to Spotify's consent screen
- `GET /auth/callback` — exchanges the code for tokens, sets a session cookie,
  redirects to the frontend `/dashboard`
- `POST /auth/logout` — clears the session
- `GET /api/me` — returns the logged-in user's Spotify profile (401 if not
  logged in)

Sessions/tokens are kept in Redis (`docker compose up -d redis`), shared with
the streaming poller so both can read/refresh the same access tokens.

## Frontend (React + Vite + TypeScript)

```bash
cd frontend
npm install
cp .env.example .env   # only needed if the backend isn't on 127.0.0.1:8000
npm run dev
```

Runs on [127.0.0.1:5173](http://127.0.0.1:5173). `/` shows a Spotify-styled "Connect with
Spotify" login screen; after auth it redirects to `/dashboard`, which fetches
`/api/me` and renders the user's avatar, display name, plan, and follower
count.

## Streaming stack (Kafka + PySpark + Airflow + Redis)

```bash
cp .env.example .env   # BQ_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS_HOST
docker compose up -d redis kafka poller
```

- `redis` — session store + hot-path "now playing" cache
- `kafka` — durable log for now-playing events (`spotify.now_playing.events`)
- `poller` (`backend/streaming/now_playing_producer.py`) — polls Spotify's
  currently-playing endpoint for active users, writes Redis + publishes Kafka
- `spark` — structured streaming job landing events into
  `raw.spotify_now_playing_events` (needs a real GCP key; see the service's
  comment in `docker-compose.yml` before starting it)
- `airflow-webserver` / `airflow-scheduler` / `airflow-postgres` — runs
  `daily_batch_ingestion` (replaces `.github/workflows/ingest.yml`) and
  `streaming_marts` (materializes the streaming dbt models + health-checks
  the poller). First run: `docker compose run --rm airflow-webserver airflow db init`
  and create an admin user before `docker compose up -d`.

## Deployment

See [deploy/README.md](deploy/README.md) for running this on a real VPS
(frontend on GitHub Pages/Vercel, everything stateful on the VPS behind Caddy).

## Next steps

- Frontend: D3.js visualizations for global trends vs. personal comparison
