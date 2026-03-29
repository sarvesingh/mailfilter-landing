"""One-time OAuth consent flow — creates token.json for Gmail + Sheets access."""

import sys
from pathlib import Path

# Add parent so we can import src.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow
from src.config import CREDENTIALS_FILE, GOOGLE_SCOPES, TOKEN_FILE


def main() -> None:
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: {CREDENTIALS_FILE} not found.")
        print("Download your OAuth Desktop client JSON from Google Cloud Console")
        print(f"and save it as {CREDENTIALS_FILE}")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE), GOOGLE_SCOPES
    )
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json())
    print(f"Token saved to {TOKEN_FILE}")
    print("You can now run: uv run python -m src.main")


if __name__ == "__main__":
    main()
