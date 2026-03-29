"""Dashboard router — server-rendered HTML endpoints. Implemented in Sprint 3."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.dependencies import get_current_user_optional
from app.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_APP_DIR = Path(__file__).resolve().parent.parent
_templates = Jinja2Templates(directory=str(_APP_DIR / "templates"))


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard_index(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """Dashboard landing page. Redirects to login if not authenticated.

    Full implementation in Sprint 3 — for now, show a placeholder.
    """
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Minimal placeholder until Sprint 3
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html><head><title>MailFilter Dashboard</title>
        <link rel="stylesheet" href="/static/style.css"></head>
        <body style="display:flex;align-items:center;justify-content:center;min-height:100vh;">
        <div class="card" style="text-align:center;padding:3rem;">
            <h1 style="color:var(--green-primary);margin-bottom:0.5rem;">Welcome, {user.name or user.email}!</h1>
            <p style="color:var(--gray-500);">Dashboard coming in Sprint 3.</p>
            <form action="/auth/logout" method="post" style="margin-top:1.5rem;">
                <button type="submit" class="btn btn-secondary">Sign out</button>
            </form>
        </div>
        </body></html>
        """,
        status_code=200,
    )
