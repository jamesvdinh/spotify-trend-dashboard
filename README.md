# Spotify Trend Dashboard

An end-to-end system that ingests Spotify listening and chart data, computes
trend signals (rising-artist velocity, chart lag, etc.), and lets users
compare their own listening habits against global trends.

This repo currently contains the **OAuth + basic profile boilerplate**:
a FastAPI backend that handles the Spotify login flow, and a React dashboard
that displays the logged-in user's profile. The streaming/ingestion/analytics
layers described in the full project spec (Kafka, PySpark, Airflow, dbt,
BigQuery, Redis) are not yet built.

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

Sessions/tokens are kept in an in-memory dict for now — swap for Redis when
wiring up the shared cache layer from the full spec.

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

## Next steps

- Ingestion: Kafka producers for listening history + chart data
- Processing: PySpark jobs, Airflow DAGs
- Warehouse: dbt models in BigQuery for trend metrics
- Serving: Redis cache in front of BigQuery, exposed via FastAPI
- Frontend: D3.js visualizations for global trends vs. personal comparison
