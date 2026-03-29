"""Gmail API: fetch Informed Delivery digest and extract mail-scan images."""

import base64
import email
import logging
from dataclasses import dataclass
from datetime import date, timedelta

from googleapiclient.discovery import build

from .config import INFORMED_DELIVERY_SENDER, get_google_credentials

logger = logging.getLogger(__name__)

MIN_IMAGE_SIZE = 5 * 1024  # 5 KB — skip tracking pixels / icons


@dataclass
class MailImage:
    data: bytes
    media_type: str
    content_id: str
    index: int


def fetch_todays_mail(target_date: date | None = None) -> list[MailImage]:
    """Fetch Informed Delivery email for *target_date* and extract mail-scan images."""
    target = target_date or date.today()
    after = target.isoformat()
    before = (target + timedelta(days=1)).isoformat()

    query = (
        f"from:{INFORMED_DELIVERY_SENDER} "
        f'subject:"Informed Delivery Daily Digest" '
        f"after:{after} before:{before}"
    )
    logger.info("Gmail query: %s", query)

    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    if not messages:
        logger.warning("No Informed Delivery email found for %s", target)
        return []

    # Use the first matching message
    msg_id = messages[0]["id"]
    logger.info("Found message %s", msg_id)

    raw_msg = (
        service.users()
        .messages()
        .get(userId="me", id=msg_id, format="raw")
        .execute()
    )
    raw_bytes = base64.urlsafe_b64decode(raw_msg["raw"])
    mime_msg = email.message_from_bytes(raw_bytes)

    return _extract_images(mime_msg)


def _extract_images(mime_msg: email.message.Message) -> list[MailImage]:
    """Walk the MIME tree and pull out mail-scan images (skip small ones)."""
    images: list[MailImage] = []
    idx = 0

    for part in mime_msg.walk():
        content_type = part.get_content_type()
        if not content_type.startswith("image/"):
            continue

        payload = part.get_payload(decode=True)
        if payload is None:
            continue

        if len(payload) < MIN_IMAGE_SIZE:
            logger.debug(
                "Skipping small image (%d bytes, cid=%s)",
                len(payload),
                part.get("Content-ID", "?"),
            )
            continue

        images.append(
            MailImage(
                data=payload,
                media_type=content_type,
                content_id=part.get("Content-ID", f"image-{idx}"),
                index=idx,
            )
        )
        idx += 1

    logger.info("Extracted %d mail-scan image(s)", len(images))
    return images
