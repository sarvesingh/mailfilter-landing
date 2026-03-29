"""FastAPI application factory and lifespan management."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.config import settings
from app.database import engine

from app.auth.router import router as auth_router
from app.mail.router import router as mail_router
from app.optout.router import router as optout_router
from app.dashboard.router import router as dashboard_router

APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    # Startup: verify DB connection
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    yield

    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="MailFilter",
    description="Stop physical junk mail. Classify, track, and opt out.",
    version="0.1.0",
    lifespan=lifespan,
)

# -- Middleware --
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        settings.APP_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Static files & templates --
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# -- Routers --
app.include_router(auth_router)
app.include_router(mail_router)
app.include_router(optout_router)
app.include_router(dashboard_router)


# -- Health check --
@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENV}
