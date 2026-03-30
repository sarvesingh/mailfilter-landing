"""Configuration: env vars, paths, and shared Google auth."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

POC_DIR = Path(__file__).resolve().parent.parent
load_dotenv(POC_DIR / ".env")

# Paths
CREDENTIALS_FILE = POC_DIR / "credentials.json"
TOKEN_FILE = POC_DIR / "token.json"
LOG_FILE = POC_DIR / "snailsense.log"

# API keys / IDs
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

# Google OAuth scopes (Gmail read-only + Sheets read/write)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

INFORMED_DELIVERY_SENDER = "USPSInformedDelivery@informeddelivery.usps.com"


def get_google_credentials() -> Credentials:
    """Load and refresh Google OAuth credentials from token.json.

    Raises RuntimeError if no valid token exists (run setup_auth.py first).
    """
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            f"No token.json found at {TOKEN_FILE}. "
            "Run: uv run python scripts/setup_auth.py"
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), GOOGLE_SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())

    if not creds.valid:
        raise RuntimeError(
            "Google credentials are invalid and could not be refreshed. "
            "Run: uv run python scripts/setup_auth.py"
        )

    return creds
