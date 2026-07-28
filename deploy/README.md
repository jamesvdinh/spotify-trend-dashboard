# Deploying to a real VPS

GitHub Pages, Vercel, and Heroku can't run this stack: Kafka, Spark, and
Airflow are long-running, stateful, multi-container services needing
persistent disk (Spark's checkpoint volume, Airflow's Postgres, Kafka's log
segments) - the opposite of static hosting or serverless functions. The
split that actually works:

- **Frontend** (static Vite build) → GitHub Pages or Vercel, where it
  genuinely fits.
- **Everything stateful** (backend, Redis, Kafka, poller, Spark, Airflow) →
  one small VPS.

## 1. Provision the VPS

A single node running Redis + Kafka + the poller + Spark + Airflow
(webserver + scheduler + Postgres) is memory-hungry. Budget at least 4GB RAM,
more comfortably 8GB - confirm actual usage once it's running rather than
guessing further.

Install Docker + Docker Compose Plugin on the VPS (see [docs.docker.com](https://docs.docker.com/engine/install/)),
then clone this repo to e.g. `/opt/spotify-trend-dashboard`.

## 2. Secrets

Nothing here gets committed - copy each example file and fill it in on the
VPS directly:

- `backend/.env` (from `backend/.env.example`) - Spotify credentials, `REDIS_URL`,
  `KAFKA_BOOTSTRAP_SERVERS`, `BQ_PROJECT_ID`.
- `.env` at the repo root (from `.env.example`) - `BQ_PROJECT_ID` and
  `GOOGLE_APPLICATION_CREDENTIALS_HOST` (used for docker-compose volume
  substitution, e.g. for the `spark` and `airflow-*` services).
- `dbt/profiles.yml` (from `dbt/profiles.yml.example`) - mounted into the
  Airflow containers, since they can't reach a developer's `~/.dbt/profiles.yml`.
- The GCP service-account key itself - `scp` it to the VPS (e.g.
  `/opt/gcp/spotify-trend-dashboard-key.json`), then point
  `GOOGLE_APPLICATION_CREDENTIALS_HOST` at that path.

## 3. Backend (systemd, not a container)

Same command as local dev, just supervised:

```bash
cd /opt/spotify-trend-dashboard/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then install `deploy/spotify-dashboard-backend.service.example` as
`/etc/systemd/system/spotify-dashboard-backend.service` (fill in the paths),
and:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now spotify-dashboard-backend
```

## 4. Everything else (docker-compose)

```bash
cd /opt/spotify-trend-dashboard
docker compose up -d redis kafka poller spark airflow-postgres
# first run only:
docker compose run --rm airflow-webserver airflow db init
docker compose run --rm airflow-webserver airflow users create \
  --username admin --firstname admin --lastname admin \
  --role Admin --email you@example.com --password <choose one>
docker compose up -d airflow-webserver airflow-scheduler
```

## 5. Reverse proxy + HTTPS

Install Caddy, copy `deploy/Caddyfile.example` to `/etc/caddy/Caddyfile`
(replace the domain), then:

```bash
sudo systemctl reload caddy
```

Only `/api` and `/auth` (the FastAPI backend) are exposed publicly. The
Airflow UI is **not** proxied - it's an operational tool, not part of the
product surface. Reach it via an SSH tunnel instead:

```bash
ssh -L 8080:127.0.0.1:8080 you@your-vps
# then open http://127.0.0.1:8080 locally
```

## 6. Firewall

Open only 80/443 (Caddy) and SSH. Kafka, Redis, and Airflow's Postgres stay
on the docker-compose-internal bridge network - never publish them on the
VPS's public interface.

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 7. Frontend on GitHub Pages

`.github/workflows/deploy-frontend.yml` builds and deploys `frontend/` on
every push to `main`. One-time setup:

- Repo Settings → Pages → Source → **GitHub Actions** (not "Deploy from a
  branch").
- Repo Settings → Secrets and variables → Actions → **Variables** → add
  `VITE_BACKEND_URL` = your VPS's public domain (e.g. `https://api.yourdomain.com`).
  It's a plain URL, not a secret, but Vite bakes it in at build time, so it
  has to be set here rather than in `backend/.env`.

The frontend uses `HashRouter` (URLs like `/#/dashboard`) specifically
because GitHub Pages has no server-side rewrites - a direct request to a real
path like `/dashboard` (e.g. the backend's post-login redirect) would 404 on
a static host.

Then point the backend and Spotify app at the deployed frontend. `FRONTEND_URL`
must be the **bare origin** (CORS matches on origin only, not path);
`FRONTEND_APP_PATH` carries the GitHub Pages project-site subpath, since the
post-login redirect needs the full path:

- `backend/.env`: `FRONTEND_URL=https://you.github.io`,
  `FRONTEND_APP_PATH=/spotify-trend-dashboard`.
- The Spotify app's registered Redirect URI (in the
  [Spotify developer dashboard](https://developer.spotify.com/dashboard)) →
  `https://api.yourdomain.com/auth/callback`.
