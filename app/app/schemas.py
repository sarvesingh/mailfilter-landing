"""Pydantic request/response schemas for the SnailSense API."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ---- Users ----


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None = None
    subscription_tier: str
    is_active: bool
    last_fetch_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Mail Pieces ----


class MailPieceResponse(BaseModel):
    id: uuid.UUID
    mail_date: date
    image_url: str | None = None
    sender: str | None = None
    mail_type: str
    is_junk: bool
    confidence: float | None = None
    classifier_notes: str | None = None
    is_stoppable: bool | None = None
    stoppable_reason: str | None = None
    user_override: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MailPieceList(BaseModel):
    items: list[MailPieceResponse]
    total: int
    page: int = 1
    page_size: int = 20


class MailCorrection(BaseModel):
    user_override: str = Field(..., pattern="^(junk|real)$")


# ---- Opt-Out ----


class OptOutRequestCreate(BaseModel):
    sender: str | None = None
    mail_piece_id: uuid.UUID | None = None


class OptOutBulkCreate(BaseModel):
    sender_names: list[str]


class OptOutRequestResponse(BaseModel):
    id: uuid.UUID
    sender: str
    channel: str
    status: str
    submitted_at: datetime | None = None
    confirmed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---- Stats ----


class StatsSummary(BaseModel):
    total_pieces: int = 0
    total_junk: int = 0
    total_real: int = 0
    junk_percentage: float = 0.0
    top_senders: list[dict[str, int]] = Field(default_factory=list)
    opt_outs_submitted: int = 0
    trees_saved: float = 0.0
    co2_avoided_lbs: float = 0.0


class WeeklyStats(BaseModel):
    weeks: list[dict[str, int | str]]


# ---- Invite Codes ----


class InviteValidation(BaseModel):
    valid: bool
