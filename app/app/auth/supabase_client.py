"""Thin Supabase client wrapper.

We use our own Google OAuth flow for login (so we get Gmail tokens), but
we keep a Supabase client around for any server-side operations that need
it (e.g. storage, or future Supabase-specific features).
"""

import logging

from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a lazily-initialized Supabase client (service-role)."""
    global _client
    if _client is None:
        _client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client


def verify_session(access_token: str) -> dict:
    """Verify a Supabase JWT and return the user payload.

    This is kept as a utility in case we ever layer Supabase Auth on top,
    but the primary auth flow uses our own signed session cookies.

    Returns the user dict from Supabase, or raises an exception if invalid.
    """
    client = get_supabase_client()
    response = client.auth.get_user(access_token)
    if response is None or response.user is None:
        raise ValueError("Invalid or expired Supabase session token")
    return {
        "id": response.user.id,
        "email": response.user.email,
        "name": response.user.user_metadata.get("name"),
    }
