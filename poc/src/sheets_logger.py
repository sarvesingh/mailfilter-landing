"""gspread: append classification rows to Google Sheet."""

import logging
from datetime import date

import gspread

from .classifier import Classification
from .config import GOOGLE_SHEET_ID, get_google_credentials

logger = logging.getLogger(__name__)


def log_results(
    classifications: list[Classification],
    message_id: str,
    target_date: date | None = None,
) -> int:
    """Append classification rows to the Google Sheet.

    Returns the number of rows added (0 if duplicates detected).
    """
    target = target_date or date.today()
    date_str = target.isoformat()

    creds = get_google_credentials()
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1

    # Duplicate detection: check if rows for this date already exist
    existing_dates = sheet.col_values(1)  # Column A = Date
    if date_str in existing_dates:
        logger.info("Rows for %s already exist — skipping", date_str)
        return 0

    rows = []
    for c in classifications:
        rows.append(
            [
                date_str,
                c.sender,
                c.mail_type,
                "Yes" if c.is_junk else "No",
                f"{c.confidence:.0%}",
                c.notes,
                "",  # Opt-Out Status (user fills manually)
                f"{message_id}:{c.image_index}",
            ]
        )

    sheet.append_rows(rows, value_input_option="USER_ENTERED")
    logger.info("Logged %d row(s) to Google Sheet for %s", len(rows), date_str)
    return len(rows)
