"""Server-side Umami event tracking for the hotspot agent.

Fire-and-forget: metrics must never block or break the request path. Events
follow the privacy rules in ``docs/agent/frontend-ux-and-analytics.md`` — no
full message text, no session tokens, no source URLs/titles, no raw IPs.

Environment overrides (all optional):

- ``UMAMI_ANALYTICS_ENABLED`` — ``true`` (default) / ``false`` to turn off.
- ``UMAMI_ENDPOINT`` — base URL of the Umami instance (no trailing slash).
- ``UMAMI_WEBSITE_ID`` — website UUID; defaults to www.hotday.uk.
- ``UMAMI_HOSTNAME`` — hostname reported for events.
- ``UMAMI_TIMEOUT_SECONDS`` — per-event send timeout.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import urllib.request

logger = logging.getLogger(__name__)

UMAMI_ENDPOINT = os.getenv(
    "UMAMI_ENDPOINT",
    "https://umami.datehoer.com",
).rstrip("/")
UMAMI_WEBSITE_ID = os.getenv(
    "UMAMI_WEBSITE_ID",
    "89135d8e-bd6e-43f7-8a2e-5e60a64db4de",  # www.hotday.uk
)
UMAMI_HOSTNAME = os.getenv("UMAMI_HOSTNAME", "www.hotday.uk")
UMAMI_ENABLED = os.getenv(
    "UMAMI_ANALYTICS_ENABLED",
    "true",
).strip().lower() in {"1", "true", "yes", "on"}
UMAMI_TIMEOUT_SECONDS = float(os.getenv("UMAMI_TIMEOUT_SECONDS", "5"))

_EVENT_NAME_MAX = 50
_USER_AGENT = "Mozilla/5.0 (hotrank-metrics)"


def _clean_name(name: str) -> str:
    """Umami truncates event names past 50 characters."""
    return name[:_EVENT_NAME_MAX]


def length_bucket(chars: int) -> str:
    """Bucket a character count to keep Umami event data low-cardinality."""
    if chars <= 20:
        return "1-20"
    if chars <= 100:
        return "21-100"
    if chars <= 500:
        return "101-500"
    if chars <= 1000:
        return "501-1000"
    if chars <= 2000:
        return "1001-2000"
    return ">2000"


def duration_bucket(ms: float) -> str:
    """Bucket a duration (ms); Umami cannot aggregate raw numeric fields."""
    if ms < 1000:
        return "<1s"
    if ms < 2000:
        return "1-2s"
    if ms < 5000:
        return "2-5s"
    if ms < 10000:
        return "5-10s"
    if ms < 30000:
        return "10-30s"
    return ">30s"


def track_event(name: str, data: dict | None = None, url: str = "/agent") -> None:
    """Queue a custom event to Umami on a daemon thread. Never raises."""
    if not UMAMI_ENABLED:
        return

    payload = {
        "type": "event",
        "payload": {
            "website": UMAMI_WEBSITE_ID,
            "hostname": UMAMI_HOSTNAME,
            "url": url,
            "name": _clean_name(name),
        },
    }
    if data:
        payload["payload"]["data"] = data

    def _send() -> None:
        try:
            request = urllib.request.Request(
                f"{UMAMI_ENDPOINT}/api/send",
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": _USER_AGENT,
                },
                method="POST",
            )
            with urllib.request.urlopen(
                request,
                timeout=UMAMI_TIMEOUT_SECONDS,
            ) as response:
                response.read()
        except Exception as exc:  # noqa: BLE001 - metrics must never raise
            logger.debug("umami track failed for %s: %s", name, exc)

    threading.Thread(target=_send, daemon=True).start()
