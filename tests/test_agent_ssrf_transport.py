import socket
import unittest
from unittest.mock import AsyncMock, patch

from hotrank.agent.safe_fetcher import (
    MAX_RESPONSE_BYTES,
    PinnedResolver,
    SafeFetchError,
    safe_fetch_text,
    validate_content_type,
)


class ValidateContentTypeTest(unittest.TestCase):
    def test_allows_known_media_types(self):
        self.assertEqual(validate_content_type("text/html"), "text/html")
        self.assertEqual(validate_content_type("TEXT/HTML"), "text/html")
        self.assertEqual(validate_content_type(" application/json "), "application/json")

    def test_rejects_unknown_media_types(self):
        for value in ("application/octet-stream", "text/css", "image/png", ""):
            with self.subTest(value=value), self.assertRaises(SafeFetchError):
                validate_content_type(value)


class PinnedResolverTest(unittest.IsolatedAsyncioTestCase):
    async def test_resolves_only_pinned_host(self):
        resolver = PinnedResolver(
            "www.36kr.com",
            [("93.184.216.34", socket.AF_INET)],
        )
        result = await resolver.resolve("www.36kr.com", 443)
        self.assertEqual(result[0]["host"], "93.184.216.34")

        with self.assertRaises(SafeFetchError):
            await resolver.resolve("evil.com", 443)


class _FakeTransport:
    def __init__(self, peer):
        self._peer = peer

    def get_extra_info(self, name):
        if name == "peername":
            return self._peer
        return None


class _FakeConnection:
    def __init__(self, peer):
        self.transport = _FakeTransport(peer)


class _FakeContent:
    def __init__(self, chunks):
        self._chunks = chunks

    async def iter_chunked(self, size):
        for chunk in self._chunks:
            yield chunk


class _FakeResponse:
    def __init__(
        self,
        *,
        status=200,
        headers=None,
        content_type="text/html",
        content_length=None,
        chunks=None,
        peer=("93.184.216.34", 443),
    ):
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type
        self.content_length = content_length
        self.connection = _FakeConnection(peer)
        self.content = _FakeContent(chunks or [])


class _FakeGetContext:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, *_args):
        return None


def _session_factory(response):
    class _FakeSession:
        def __init__(self, **_kwargs):
            self._response = response

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        def get(self, url, allow_redirects=False):
            return _FakeGetContext(self._response)

    return _FakeSession


class SafeFetcherTransportTest(unittest.IsolatedAsyncioTestCase):
    def _patches(self, response, addresses=("93.184.216.34", socket.AF_INET)):
        return (
            patch(
                "hotrank.agent.safe_fetcher.resolve_public_addresses",
                AsyncMock(return_value=[addresses]),
            ),
            patch(
                "hotrank.agent.safe_fetcher.aiohttp.ClientSession",
                _session_factory(response),
            ),
        )

    async def test_rejects_disallowed_content_type(self):
        with patch(
            "hotrank.agent.safe_fetcher.resolve_public_addresses",
            AsyncMock(return_value=[("93.184.216.34", socket.AF_INET)]),
        ), patch(
            "hotrank.agent.safe_fetcher.aiohttp.ClientSession",
            _session_factory(
                _FakeResponse(content_type="application/octet-stream")
            ),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")

    async def test_rejects_oversized_content_length_header(self):
        with patch(
            "hotrank.agent.safe_fetcher.resolve_public_addresses",
            AsyncMock(return_value=[("93.184.216.34", socket.AF_INET)]),
        ), patch(
            "hotrank.agent.safe_fetcher.aiohttp.ClientSession",
            _session_factory(
                _FakeResponse(
                    content_type="text/html",
                    content_length=MAX_RESPONSE_BYTES + 1,
                )
            ),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")

    async def test_rejects_oversized_streamed_body(self):
        with patch(
            "hotrank.agent.safe_fetcher.resolve_public_addresses",
            AsyncMock(return_value=[("93.184.216.34", socket.AF_INET)]),
        ), patch(
            "hotrank.agent.safe_fetcher.aiohttp.ClientSession",
            _session_factory(
                _FakeResponse(
                    content_type="text/html",
                    content_length=None,
                    chunks=[b"x" * (MAX_RESPONSE_BYTES + 1)],
                )
            ),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")

    async def test_rejects_peer_mismatch_after_resolution(self):
        # DNS resolved to 93.184.216.34, but the actual connection peer
        # differs. The fetcher must reject the changed peer.
        with patch(
            "hotrank.agent.safe_fetcher.resolve_public_addresses",
            AsyncMock(return_value=[("93.184.216.34", socket.AF_INET)]),
        ), patch(
            "hotrank.agent.safe_fetcher.aiohttp.ClientSession",
            _session_factory(
                _FakeResponse(peer=("8.8.8.8", 443))
            ),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")

    async def test_rejects_multihop_redirect_to_private(self):
        with patch(
            "hotrank.agent.safe_fetcher._request_once",
            AsyncMock(side_effect=[
                (302, {}, "https://www.36kr.com/next", b""),
                (302, {}, "http://127.0.0.1/admin", b""),
            ]),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")

    async def test_rejects_redirect_beyond_limit(self):
        redirects = [
            (302, {}, f"https://www.36kr.com/hop{i}", b"")
            for i in range(4)
        ]
        with patch(
            "hotrank.agent.safe_fetcher._request_once",
            AsyncMock(side_effect=redirects),
        ):
            with self.assertRaises(SafeFetchError):
                await safe_fetch_text("https://www.36kr.com/news", "36kr")


if __name__ == "__main__":
    unittest.main()
