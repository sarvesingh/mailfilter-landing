"""Auth router — /auth/* endpoints for Google OAuth login with invite codes."""

import asyncio
import logging
import urllib.parse
from datetime import datetime, timezone
from functools import partial
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.google_tokens import GOOGLE_SCOPES, encrypt_token
from app.auth.session import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
    decode_session_token,
)
from app.config import settings
from app.database import get_db
from app.models import InviteCode, User
from app.schemas import InviteValidation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

_APP_DIR = Path(__file__).resolve().parent.parent
_templates = Jinja2Templates(directory=str(_APP_DIR / "templates"))


def _build_google_flow(state: str | None = None) -> Flow:
    """Create a google_auth_oauthlib Flow configured from settings."""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_SCOPES,
        state=state,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow


def _is_production() -> bool:
    return settings.ENV == "production"


# --------------------------------------------------------------------------- #
# GET /auth/login — login page
# --------------------------------------------------------------------------- #


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    """Render the login page.

    If the user already has a valid session, redirect to /dashboard.
    """
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie and decode_session_token(cookie) is not None:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    return _templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error},
    )


# --------------------------------------------------------------------------- #
# GET /auth/validate-invite — JSON endpoint to check invite code
# --------------------------------------------------------------------------- #


@router.get("/validate-invite", response_model=InviteValidation)
async def validate_invite(
    code: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Check whether an invite code is valid and has remaining uses."""
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == code.strip().upper())
    )
    invite = result.scalar_one_or_none()

    if invite is None:
        return InviteValidation(valid=False)

    return InviteValidation(valid=invite.times_used < invite.max_uses)


# --------------------------------------------------------------------------- #
# GET /auth/google — start Google OAuth flow
# --------------------------------------------------------------------------- #


@router.get("/google")
async def google_auth_start(
    invite_code: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Validate the invite code, then redirect to Google OAuth consent screen."""
    code_value = invite_code.strip().upper()

    # Validate invite code
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == code_value)
    )
    invite = result.scalar_one_or_none()

    if invite is None or invite.times_used >= invite.max_uses:
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Invalid or exhausted invite code."),
            status_code=status.HTTP_302_FOUND,
        )

    # Build the OAuth flow. Encode invite_code in the state parameter so we
    # can retrieve it in the callback.
    flow = _build_google_flow(state=code_value)

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


# --------------------------------------------------------------------------- #
# GET /auth/callback — Google OAuth callback
# --------------------------------------------------------------------------- #


@router.get("/callback")
async def google_auth_callback(
    request: Request,
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Exchange the Google auth code for tokens, create/update User, set session cookie."""

    # Handle Google-side errors
    if error:
        logger.warning("Google OAuth error: %s", error)
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote(f"Google authentication failed: {error}"),
            status_code=status.HTTP_302_FOUND,
        )

    if not code:
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Missing authorization code from Google."),
            status_code=status.HTTP_302_FOUND,
        )

    # The state parameter carries the invite code
    invite_code_value = (state or "").strip().upper()
    if not invite_code_value:
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Invalid OAuth state — missing invite code."),
            status_code=status.HTTP_302_FOUND,
        )

    # Re-validate the invite code (prevents replay after code is exhausted)
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == invite_code_value)
    )
    invite = result.scalar_one_or_none()

    # ------------------------------------------------------------------ #
    # Exchange authorization code for tokens
    # ------------------------------------------------------------------ #
    try:
        flow = _build_google_flow(state=invite_code_value)
        # flow.fetch_token is a synchronous HTTP call — run in thread pool
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(flow.fetch_token, code=code))
    except Exception as exc:
        logger.exception("Token exchange failed")
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Failed to complete Google sign-in. Please try again."),
            status_code=status.HTTP_302_FOUND,
        )

    credentials = flow.credentials

    # Extract user info from the id_token
    # google-auth-oauthlib already verifies the id_token during fetch_token
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    try:
        id_info = await loop.run_in_executor(
            None,
            partial(
                google_id_token.verify_oauth2_token,
                credentials.id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            ),
        )
    except Exception:
        logger.exception("Failed to verify id_token")
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Failed to verify your Google identity."),
            status_code=status.HTTP_302_FOUND,
        )

    email = id_info.get("email")
    name = id_info.get("name")

    if not email:
        return RedirectResponse(
            url="/auth/login?error=" + urllib.parse.quote("Could not retrieve your email from Google."),
            status_code=status.HTTP_302_FOUND,
        )

    # ------------------------------------------------------------------ #
    # Create or update User
    # ------------------------------------------------------------------ #
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    encrypted_access = encrypt_token(credentials.token)
    encrypted_refresh = encrypt_token(credentials.refresh_token) if credentials.refresh_token else None

    token_expiry = None
    if credentials.expiry:
        token_expiry = credentials.expiry.replace(tzinfo=timezone.utc)

    is_new_user = user is None

    if user is None:
        user = User(
            email=email,
            name=name,
            google_access_token=encrypted_access,
            google_refresh_token=encrypted_refresh,
            google_token_expires_at=token_expiry,
            invite_code=invite_code_value,
        )
        db.add(user)
    else:
        # Returning user — update tokens
        user.name = name or user.name
        user.google_access_token = encrypted_access
        if encrypted_refresh:
            user.google_refresh_token = encrypted_refresh
        user.google_token_expires_at = token_expiry
        user.updated_at = datetime.now(timezone.utc)
        # Keep the original invite code, don't overwrite

    await db.flush()  # Ensure user.id is populated

    # ------------------------------------------------------------------ #
    # Update invite code usage (only for new users)
    # ------------------------------------------------------------------ #
    if is_new_user and invite is not None and invite.times_used < invite.max_uses:
        invite.times_used += 1

    await db.commit()
    await db.refresh(user)

    # ------------------------------------------------------------------ #
    # Set session cookie and redirect to dashboard
    # ------------------------------------------------------------------ #
    session_token = create_session_token({"user_id": str(user.id)})

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=_is_production(),
        path="/",
    )

    logger.info(
        "User %s (%s) logged in successfully (new=%s)",
        user.id,
        email,
        is_new_user,
    )

    return response


# --------------------------------------------------------------------------- #
# POST /auth/logout
# --------------------------------------------------------------------------- #


@router.post("/logout")
async def logout():
    """Clear the session cookie and redirect to landing page."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_is_production(),
    )
    return response
