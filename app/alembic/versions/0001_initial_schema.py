"""Initial schema — all tables for SnailSense MVP.

Revision ID: 0001
Revises:
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- users --
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("google_access_token", sa.Text(), nullable=True),
        sa.Column("google_refresh_token", sa.Text(), nullable=True),
        sa.Column("google_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supabase_user_id", sa.Text(), nullable=True, unique=True),
        sa.Column("subscription_tier", sa.Text(), server_default=sa.text("'pro'"), nullable=False),
        sa.Column("invite_code", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_fetch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # -- invite_codes --
    op.create_table(
        "invite_codes",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("code", sa.Text(), nullable=False, unique=True),
        sa.Column("max_uses", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("times_used", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # -- mail_pieces --
    op.create_table(
        "mail_pieces",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("mail_date", sa.Date(), nullable=False),
        sa.Column("gmail_message_id", sa.Text(), nullable=True),
        sa.Column("image_index", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("sender", sa.Text(), nullable=True),
        sa.Column("mail_type", sa.Text(), nullable=False),
        sa.Column("is_junk", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("classifier_notes", sa.Text(), nullable=True),
        sa.Column("is_stoppable", sa.Boolean(), nullable=True),
        sa.Column("stoppable_reason", sa.Text(), nullable=True),
        sa.Column("user_override", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "gmail_message_id", "image_index"),
    )
    op.create_index("ix_mail_pieces_user_date", "mail_pieces", ["user_id", "mail_date"])
    op.create_index("ix_mail_pieces_user_sender", "mail_pieces", ["user_id", "sender"])
    op.create_index("ix_mail_pieces_user_junk", "mail_pieces", ["user_id", "is_junk"])

    # -- opt_out_requests --
    op.create_table(
        "opt_out_requests",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sender", sa.Text(), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), server_default=sa.text("'queued'"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_optout_user_status", "opt_out_requests", ["user_id", "status"])
    op.create_index("ix_optout_user_sender", "opt_out_requests", ["user_id", "sender"])

    # -- sender_directory --
    op.create_table(
        "sender_directory",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("sender_name", sa.Text(), nullable=False, unique=True),
        sa.Column("sender_aliases", ARRAY(sa.Text()), nullable=True),
        sa.Column("is_stoppable", sa.Boolean(), nullable=False),
        sa.Column("opt_out_channels", ARRAY(sa.Text()), nullable=True),
        sa.Column("opt_out_url", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # -- daily_stats --
    op.create_table(
        "daily_stats",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_pieces", sa.Integer(), nullable=True),
        sa.Column("junk_count", sa.Integer(), nullable=True),
        sa.Column("real_count", sa.Integer(), nullable=True),
        sa.Column("stoppable_count", sa.Integer(), nullable=True),
        sa.UniqueConstraint("user_id", "date"),
    )


def downgrade() -> None:
    op.drop_table("daily_stats")
    op.drop_table("sender_directory")
    op.drop_index("ix_optout_user_sender", table_name="opt_out_requests")
    op.drop_index("ix_optout_user_status", table_name="opt_out_requests")
    op.drop_table("opt_out_requests")
    op.drop_index("ix_mail_pieces_user_junk", table_name="mail_pieces")
    op.drop_index("ix_mail_pieces_user_sender", table_name="mail_pieces")
    op.drop_index("ix_mail_pieces_user_date", table_name="mail_pieces")
    op.drop_table("mail_pieces")
    op.drop_table("invite_codes")
    op.drop_table("users")
