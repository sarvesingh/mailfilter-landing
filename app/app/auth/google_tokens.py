"""Google OAuth token encryption, decryption, and credential management."""

import asyncio
import logging
from datetime import datetime, timezone
from functools import partial

from cryptography.fernet import Fernet, InvalidToken
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)

_fernet = Fernet(settings.FERNET_KEY.encode())

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def encrypt_token(token: str) -> str:
    """Encrypt a plaintext token with Fernet.

    Returns a URL-safe base64-encoded ciphertext string.
    """
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    """Decrypt a Fernet-encrypted token.

    Raises ValueError if the token is invalid or corrupted.
    """
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt token — key mismatch or corrupted data") from exc


async def get_user_gmail_credentials(
    user: User,
    db: AsyncSession,
) -> Credentials:
    """Build a ready-to-use Google Credentials object for the given user.

    If the access token is expired and a refresh token is available, the
    credentials are refreshed automatically and the new tokens are persisted
    back to the database (encrypted).

    Raises ValueError if required tokens are missing or decryption fails.
    Raises google.auth.exceptions.RefreshError if the refresh token has been
    revoked or is otherwise invalid.
    """
    if not user.google_access_token:
        raise ValueError(f"User {user.id} has no stored Google access token")
    if not user.google_refresh_token:
        raise ValueError(f"User {user.id} has no stored Google refresh token")

    access_token = decrypt_token(user.google_access_token)
    refresh_token = decrypt_token(user.google_refresh_token)

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=GOOGLE_SCOPES,
    )

    # Set expiry so the library knows whether to refresh
    if user.google_token_expires_at:
        creds.expiry = user.google_token_expires_at.replace(tzinfo=None)

    if creds.expired or not creds.valid:
        logger.info("Refreshing expired Google credentials for user %s", user.id)
        # creds.refresh() is a synchronous blocking HTTP call — run it in a
        # thread pool so we don't block the async event loop.
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(creds.refresh, Request()))

        # Persist the refreshed tokens
        user.google_access_token = encrypt_token(creds.token)
        if creds.refresh_token:
            # Google sometimes rotates the refresh token
            user.google_refresh_token = encrypt_token(creds.refresh_token)
        if creds.expiry:
            user.google_token_expires_at = creds.expiry.replace(tzinfo=timezone.utc)

        db.add(user)
        await db.commit()
        logger.info("Persisted refreshed tokens for user %s", user.id)

    return creds
