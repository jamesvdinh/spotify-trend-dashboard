from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import api, auth

settings = get_settings()

app = FastAPI(title="Spotify Trend Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(api.router)


@app.get("/health")
def health():
    return {"status": "ok"}
