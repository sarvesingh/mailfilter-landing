"""Session cookie management using itsdangerous signed cookies."""

import logging
from typing import Any

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import settings

logger = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "snailsense_session"
SESSION_MAX_AGE_SECONDS = 30 * 24 * 60 * 60  # 30 days

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def create_session_token(payload: dict[str, Any]) -> str:
    """Sign a payload dict into a URL-safe session token string."""
    return _serializer.dumps(payload)


def decode_session_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a session token.

    Returns the payload dict, or None if the token is invalid/expired.
    """
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return data
    except SignatureExpired:
        logger.warning("Session token expired")
        return None
    except BadSignature:
        logger.warning("Invalid session token signature")
        return None
