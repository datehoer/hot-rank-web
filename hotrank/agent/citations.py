import base64
import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from hotrank.agent.safe_fetcher import SafeFetchError, validate_source_url


SOURCE_MARKER_RE = re.compile(
    r"\[\[source:([^\]\s]{1,128})\]\]"
)


def normalize_source_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme.lower() not in {"http", "https"}:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        if not parsed.hostname:
            return None

        hostname = parsed.hostname.encode("idna").decode("ascii").lower()
        port = parsed.port
        default_port = 80 if parsed.scheme.lower() == "http" else 443
        netloc = hostname if port in {None, default_port} else f"{hostname}:{port}"
        return urlunsplit(
            (
                parsed.scheme.lower(),
                netloc,
                parsed.path or "/",
                parsed.query,
                "",
            )
        )
    except (UnicodeError, ValueError):
        return None


@dataclass
class CitationRecord:
    source_id: str
    topic_id: int
    title: str
    url: str
    platform: str
    hot_value: str | None = None
    rank_updated_at: str | None = None
    detail_status: str = "title_only"

    def to_event(self, number: int) -> dict[str, object]:
        return {
            "number": number,
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "platform": self.platform,
            "hot_value": self.hot_value,
            "rank_updated_at": self.rank_updated_at,
            "detail_status": self.detail_status,
        }


class CitationRegistry:
    def __init__(self, secret: bytes | None = None) -> None:
        self._secret = secret or secrets.token_bytes(32)
        self._records: dict[str, CitationRecord] = {}

    def register(
        self,
        *,
        topic_id: int,
        title: object,
        url: object,
        platform: object,
        hot_value: object = None,
        rank_updated_at: object = None,
        detail_status: str = "title_only",
    ) -> str | None:
        normalized_url = normalize_source_url(url)
        if normalized_url is None or not isinstance(platform, str):
            return None
        try:
            normalized_url = validate_source_url(
                normalized_url,
                platform,
            ).url
        except SafeFetchError:
            return None

        message = f"{topic_id}\0{normalized_url}".encode("utf-8")
        digest = hmac.new(
            self._secret,
            message,
            hashlib.sha256,
        ).digest()[:16]
        encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        source_id = f"src_{encoded}"

        existing = self._records.get(source_id)
        if existing is not None and detail_status == "fetched":
            existing.detail_status = "fetched"
            return source_id

        self._records[source_id] = CitationRecord(
            source_id=source_id,
            topic_id=topic_id,
            title=str(title or "Untitled")[:300],
            url=normalized_url,
            platform=platform[:80],
            hot_value=(
                str(hot_value)[:100]
                if hot_value is not None
                else None
            ),
            rank_updated_at=(
                str(rank_updated_at)[:100]
                if rank_updated_at is not None
                else None
            ),
            detail_status=detail_status,
        )
        return source_id

    def resolve_answer(
        self,
        answer: str,
    ) -> tuple[str, list[dict[str, object]]]:
        ordered_ids: list[str] = []

        def replace_marker(match: re.Match[str]) -> str:
            source_id = match.group(1)
            if source_id not in self._records:
                return ""
            if source_id not in ordered_ids:
                ordered_ids.append(source_id)
            return f"[{ordered_ids.index(source_id) + 1}]"

        cleaned_answer = SOURCE_MARKER_RE.sub(replace_marker, answer)
        citations = [
            self._records[source_id].to_event(number)
            for number, source_id in enumerate(ordered_ids, start=1)
        ]
        return cleaned_answer, citations

    def registered_source_ids(self) -> list[str]:
        """Return the source ids registered during this run, in order."""
        return list(self._records.keys())
