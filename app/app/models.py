"""SQLAlchemy ORM models — all tables for SnailSense."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    supabase_user_id: Mapped[str | None] = mapped_column(
        Text, unique=True, nullable=True
    )
    subscription_tier: Mapped[str] = mapped_column(
        Text, server_default=text("'pro'"), nullable=False
    )
    invite_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )
    last_fetch_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relationships
    mail_pieces: Mapped[list["MailPiece"]] = relationship(back_populates="user")
    opt_out_requests: Mapped[list["OptOutRequest"]] = relationship(
        back_populates="user"
    )
    daily_stats: Mapped[list["DailyStat"]] = relationship(back_populates="user")


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    max_uses: Mapped[int] = mapped_column(
        Integer, server_default=text("1"), nullable=False
    )
    times_used: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class MailPiece(Base):
    __tablename__ = "mail_pieces"
    __table_args__ = (
        UniqueConstraint("user_id", "gmail_message_id", "image_index"),
        Index("ix_mail_pieces_user_date", "user_id", "mail_date"),
        Index("ix_mail_pieces_user_sender", "user_id", "sender"),
        Index("ix_mail_pieces_user_junk", "user_id", "is_junk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    mail_date: Mapped[date] = mapped_column(Date, nullable=False)
    gmail_message_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender: Mapped[str | None] = mapped_column(Text, nullable=True)
    mail_type: Mapped[str] = mapped_column(Text, nullable=False)
    is_junk: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    classifier_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_stoppable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    stoppable_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="mail_pieces")


class OptOutRequest(Base):
    __tablename__ = "opt_out_requests"
    __table_args__ = (
        Index("ix_optout_user_status", "user_id", "status"),
        Index("ix_optout_user_sender", "user_id", "sender"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, server_default=text("'queued'"), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="opt_out_requests")


class SenderDirectory(Base):
    __tablename__ = "sender_directory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    sender_name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    sender_aliases: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    is_stoppable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    opt_out_channels: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    opt_out_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class DailyStat(Base):
    __tablename__ = "daily_stats"
    __table_args__ = (UniqueConstraint("user_id", "date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_pieces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    junk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    real_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stoppable_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="daily_stats")
