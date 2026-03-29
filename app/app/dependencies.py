"""FastAPI dependencies — auth, DB session, etc."""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User


async def get_current_user(
    session_token: str | None = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Read session cookie / JWT and return the authenticated User.

    Stub implementation — will be wired to Supabase Auth in Sprint 1.
    """
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # TODO (Sprint 1): Validate session_token against Supabase Auth,
    # look up User by supabase_user_id, return the ORM object.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Auth not implemented yet",
    )
