"""Claude vision API: classify each mail-piece image."""

import base64
import json
import logging
import re
from dataclasses import dataclass

import anthropic

from .config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from .gmail_reader import MailImage

logger = logging.getLogger(__name__)

VALID_MAIL_TYPES = {
    "bill_or_statement",
    "personal_letter",
    "government_official",
    "credit_card_offer",
    "insurance_offer",
    "catalog",
    "coupon_flyer",
    "political_mailer",
    "charity_solicitation",
    "subscription_renewal",
    "other_junk",
    "other_real",
    "unreadable",
}

SYSTEM_PROMPT = """\
You are a mail classifier. You will receive a scanned image of a physical mail piece \
from USPS Informed Delivery.

Analyze the image and return a JSON object with these fields:
- "sender": best guess at who sent the mail (company or person name)
- "mail_type": one of: bill_or_statement, personal_letter, government_official, \
credit_card_offer, insurance_offer, catalog, coupon_flyer, political_mailer, \
charity_solicitation, subscription_renewal, other_junk, other_real, unreadable
- "is_junk": true if this is unsolicited marketing/junk mail, false otherwise
- "confidence": a number from 0.0 to 1.0
- "notes": brief explanation of your classification

Return ONLY the JSON object, no other text."""


@dataclass
class Classification:
    sender: str
    mail_type: str
    is_junk: bool
    confidence: float
    notes: str
    image_index: int


def classify_all(images: list[MailImage]) -> list[Classification]:
    """Classify each mail image with Claude's vision API."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results: list[Classification] = []

    for img in images:
        logger.info("Classifying image %d (cid=%s)", img.index, img.content_id)
        try:
            result = _classify_one(client, img)
            results.append(result)
        except Exception:
            logger.exception("Failed to classify image %d", img.index)
            results.append(
                Classification(
                    sender="unknown",
                    mail_type="unreadable",
                    is_junk=False,
                    confidence=0.0,
                    notes="Classification failed — see logs",
                    image_index=img.index,
                )
            )

    return results


def _classify_one(client: anthropic.Anthropic, img: MailImage) -> Classification:
    """Send one image to Claude and parse the classification response."""
    b64_data = base64.standard_b64encode(img.data).decode()

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img.media_type,
                            "data": b64_data,
                        },
                    },
                    {"type": "text", "text": "Classify this mail piece."},
                ],
            }
        ],
    )

    raw_text = response.content[0].text
    parsed = _parse_json_response(raw_text)

    mail_type = parsed.get("mail_type", "unreadable")
    if mail_type not in VALID_MAIL_TYPES:
        logger.warning("Unknown mail_type '%s', defaulting to 'unreadable'", mail_type)
        mail_type = "unreadable"

    return Classification(
        sender=parsed.get("sender", "unknown"),
        mail_type=mail_type,
        is_junk=bool(parsed.get("is_junk", False)),
        confidence=float(parsed.get("confidence", 0.0)),
        notes=parsed.get("notes", ""),
        image_index=img.index,
    )


def _parse_json_response(text: str) -> dict:
    """Parse JSON from Claude's response, handling markdown fences."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code fence
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    logger.error("Could not parse JSON from response: %s", text[:200])
    return {}
