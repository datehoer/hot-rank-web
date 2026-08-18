import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, urlunsplit

import aiohttp
from aiohttp.abc import AbstractResolver


MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 3
ALLOWED_CONTENT_TYPES = {
    "application/json",
    "application/xhtml+xml",
    "text/html",
    "text/plain",
}
ALLOWED_SOURCE_HOSTS = {
    "36kr": {"36kr.com", "www.36kr.com", "m.36kr.com"},
    "ithome": {"ithome.com", "www.ithome.com", "m.ithome.com"},
    "pengpai": {"thepaper.cn", "www.thepaper.cn", "m.thepaper.cn"},
    "shaoshupai_hot": {"sspai.com", "www.sspai.com"},
    "wallstreetcn": {
        "wallstreetcn.com",
        "www.wallstreetcn.com",
        "api-one-wscn.awtmt.com",
    },
}


class SafeFetchError(RuntimeError):
    """A source request was rejected or failed without exposing internals."""


@dataclass(frozen=True)
class ValidatedURL:
    url: str
    hostname: str
    port: int


def _normalize_hostname(hostname: str) -> str:
    try:
        return hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise SafeFetchError("Source URL host is invalid.") from exc


def validate_source_url(url: object, platform: str) -> ValidatedURL:
    if not isinstance(url, str) or not url.strip():
        raise SafeFetchError("Source URL is empty.")

    try:
        parsed = urlsplit(url.strip())
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"}:
            raise SafeFetchError("Source URL scheme is not allowed.")
        if parsed.username is not None or parsed.password is not None:
            raise SafeFetchError("Source URL credentials are not allowed.")
        if not parsed.hostname:
            raise SafeFetchError("Source URL host is missing.")

        hostname = _normalize_hostname(parsed.hostname)
        allowed_hosts = ALLOWED_SOURCE_HOSTS.get(platform, set())
        if hostname not in allowed_hosts:
            raise SafeFetchError("Source URL host is not allowed.")

        default_port = 80 if scheme == "http" else 443
        port = parsed.port or default_port
        if port != default_port:
            raise SafeFetchError("Source URL port is not allowed.")

        netloc = hostname
        normalized_url = urlunsplit(
            (scheme, netloc, parsed.path or "/", parsed.query, "")
        )
        return ValidatedURL(normalized_url, hostname, port)
    except SafeFetchError:
        raise
    except (UnicodeError, ValueError) as exc:
        raise SafeFetchError("Source URL is invalid.") from exc


def validate_public_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise SafeFetchError("Source address is invalid.") from exc
    if not address.is_global:
        raise SafeFetchError("Source address is not public.")
    # ``is_global`` does not classify multicast as private/reserved, so it
    # must be rejected explicitly to match the threat model boundary.
    if address.is_multicast:
        raise SafeFetchError("Source address is multicast.")
    return address


async def resolve_public_addresses(
    hostname: str,
    port: int,
) -> list[tuple[str, int]]:
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(
            hostname,
            port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except OSError as exc:
        raise SafeFetchError("Source host could not be resolved.") from exc

    addresses: list[tuple[str, int]] = []
    seen: set[str] = set()
    for family, _, _, _, sockaddr in infos:
        address_text = sockaddr[0]
        validate_public_ip(address_text)
        if address_text not in seen:
            addresses.append((address_text, family))
            seen.add(address_text)
    if not addresses:
        raise SafeFetchError("Source host has no usable address.")
    return addresses


class PinnedResolver(AbstractResolver):
    def __init__(
        self,
        hostname: str,
        addresses: list[tuple[str, int]],
    ) -> None:
        self._hostname = hostname
        self._addresses = addresses

    async def resolve(
        self,
        host: str,
        port: int = 0,
        family: int = socket.AF_INET,
    ) -> list[dict[str, object]]:
        if _normalize_hostname(host) != self._hostname:
            raise SafeFetchError("Unexpected source host resolution.")
        return [
            {
                "hostname": host,
                "host": address,
                "port": port,
                "family": address_family,
                "proto": 0,
                "flags": socket.AI_NUMERICHOST,
            }
            for address, address_family in self._addresses
        ]

    async def close(self) -> None:
        return None


def _validate_peer(
    response: aiohttp.ClientResponse,
    allowed_addresses: list[tuple[str, int]],
) -> None:
    connection = response.connection
    transport = connection.transport if connection is not None else None
    peer = transport.get_extra_info("peername") if transport is not None else None
    if not peer:
        raise SafeFetchError("Source connection peer is unavailable.")
    peer_address = validate_public_ip(str(peer[0]))
    expected_addresses = {
        validate_public_ip(address)
        for address, _ in allowed_addresses
    }
    if peer_address not in expected_addresses:
        raise SafeFetchError("Source connection peer changed after validation.")


def validate_content_type(content_type: str) -> str:
    normalized = (content_type or "").strip().lower()
    if normalized not in ALLOWED_CONTENT_TYPES:
        raise SafeFetchError("Source content type is not allowed.")
    return normalized


async def _request_once(
    target: ValidatedURL,
) -> tuple[int, dict[str, str], str | None, bytes]:
    addresses = await resolve_public_addresses(target.hostname, target.port)
    resolver = PinnedResolver(target.hostname, addresses)
    connector = aiohttp.TCPConnector(
        resolver=resolver,
        use_dns_cache=False,
        limit=4,
    )
    timeout = aiohttp.ClientTimeout(
        total=8,
        sock_connect=3,
        sock_read=5,
    )

    try:
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            trust_env=False,
            auto_decompress=True,
            headers={"User-Agent": "HotDay-Agent/1.0"},
        ) as client:
            async with client.get(
                target.url,
                allow_redirects=False,
            ) as response:
                _validate_peer(response, addresses)
                headers = {key.lower(): value for key, value in response.headers.items()}
                location = response.headers.get("Location")
                if 300 <= response.status < 400:
                    return response.status, headers, location, b""
                if response.status < 200 or response.status >= 300:
                    raise SafeFetchError("Source returned an unsuccessful status.")
                validate_content_type(response.content_type)

                content_length = response.content_length
                if content_length is not None and content_length > MAX_RESPONSE_BYTES:
                    raise SafeFetchError("Source response is too large.")

                body = bytearray()
                async for chunk in response.content.iter_chunked(64 * 1024):
                    body.extend(chunk)
                    if len(body) > MAX_RESPONSE_BYTES:
                        raise SafeFetchError("Source response is too large.")
                return response.status, headers, location, bytes(body)
    except SafeFetchError:
        raise
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise SafeFetchError("Source request failed.") from exc


async def safe_fetch_text(url: object, platform: str) -> str:
    current = validate_source_url(url, platform)
    for redirect_count in range(MAX_REDIRECTS + 1):
        status, headers, location, body = await _request_once(current)
        if not 300 <= status < 400:
            content_type = headers.get("content-type", "")
            charset = "utf-8"
            for part in content_type.split(";")[1:]:
                key, _, value = part.strip().partition("=")
                if key.lower() == "charset" and value:
                    charset = value.strip('"\'')
                    break
            try:
                return body.decode(charset, errors="replace")
            except LookupError:
                return body.decode("utf-8", errors="replace")

        if location is None:
            raise SafeFetchError("Source redirect location is missing.")
        if redirect_count >= MAX_REDIRECTS:
            raise SafeFetchError("Source redirect limit exceeded.")
        current = validate_source_url(
            urljoin(current.url, location),
            platform,
        )

    raise SafeFetchError("Source redirect limit exceeded.")
