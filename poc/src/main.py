"""Orchestrator: fetch email → extract images → classify → log to Sheets."""

import logging
import sys
from datetime import date

from .config import LOG_FILE
from .gmail_reader import fetch_todays_mail
from .classifier import classify_all
from .sheets_logger import log_results

logger = logging.getLogger("snailsense")


def setup_logging() -> None:
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s  %(message)s")

    # File handler
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Stdout handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # Also capture sub-module loggers under "snailsense"
    for name in ("src.gmail_reader", "src.classifier", "src.sheets_logger", "src.config"):
        sub = logging.getLogger(name)
        sub.setLevel(logging.DEBUG)
        sub.addHandler(fh)
        sub.addHandler(sh)


def main() -> None:
    setup_logging()

    # Optional date argument: YYYY-MM-DD
    target_date = None
    if len(sys.argv) > 1:
        try:
            target_date = date.fromisoformat(sys.argv[1])
            logger.info("Using target date: %s", target_date)
        except ValueError:
            logger.error("Invalid date format: %s (expected YYYY-MM-DD)", sys.argv[1])
            sys.exit(1)

    # 1. Fetch email
    logger.info("Fetching Informed Delivery email...")
    images = fetch_todays_mail(target_date)
    if not images:
        logger.info("No mail images found — done (Sunday/holiday or no email yet).")
        return

    # 2. Classify images
    logger.info("Classifying %d image(s) with Claude...", len(images))
    classifications = classify_all(images)

    # 3. Log to Google Sheets
    logger.info("Logging results to Google Sheet...")
    # Build a message ID from date for dedup tracking
    target = target_date or date.today()
    message_id = f"informed-delivery-{target.isoformat()}"
    rows_added = log_results(classifications, message_id, target_date)

    if rows_added:
        logger.info("Done — %d row(s) added to sheet.", rows_added)
    else:
        logger.info("Done — no new rows (already logged for this date).")

    # Summary
    junk_count = sum(1 for c in classifications if c.is_junk)
    real_count = len(classifications) - junk_count
    logger.info("Summary: %d junk, %d real mail", junk_count, real_count)


if __name__ == "__main__":
    main()
