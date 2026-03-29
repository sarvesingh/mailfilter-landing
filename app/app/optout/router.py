"""Opt-out router — /api/optout/* endpoints. Implemented in Sprint 5."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/optout", tags=["optout"])
