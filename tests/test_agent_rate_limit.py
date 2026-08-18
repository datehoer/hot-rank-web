import hashlib
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

from app import app
from hotrank.infrastructure import limiter
from hotrank.routers.agent import agent_session_rate_limit_key


async def _completed_agent_response(*_args, **_kwargs):
    yield 'event: done\ndata: {"usage": {}}\n\n'


class AgentRateLimitTest(unittest.TestCase):
    def setUp(self):
        self._storage = limiter._storage
        self._strategy = limiter._limiter
        self._storage_dead = limiter._storage_dead
        self._enabled = limiter.enabled
        limiter._storage = MemoryStorage()
        limiter._limiter = FixedWindowRateLimiter(limiter._storage)
        limiter._storage_dead = False
        limiter.enabled = True

    def tearDown(self):
        limiter._storage = self._storage
        limiter._limiter = self._strategy
        limiter._storage_dead = self._storage_dead
        limiter.enabled = self._enabled

    @staticmethod
    def _payload(session_id: str) -> dict[str, object]:
        return {
            "role": "user",
            "content": "hello",
            "platform": ["36kr"],
            "timestamp": 1,
            "session_id": session_id,
        }

    def _post(self, client: TestClient, session_id: str):
        with patch(
            "hotrank.routers.agent.get_allowed_query_sources",
            AsyncMock(return_value=["36kr"]),
        ), patch(
            "hotrank.routers.agent.agent_response",
            _completed_agent_response,
        ):
            return client.post(
                f"/agent/sessions/{session_id}/message",
                json=self._payload(session_id),
                headers={"Accept": "text/event-stream"},
            )

    def test_session_key_is_hashed_and_bounded(self):
        session_id = "private-session-value"

        class FakeRequest:
            path_params = {"session_id": session_id}

        key = agent_session_rate_limit_key(FakeRequest())
        self.assertEqual(
            key,
            "agent-session:"
            + hashlib.sha256(session_id.encode("utf-8")).hexdigest(),
        )
        self.assertNotIn(session_id, key)

    def test_ip_limit_returns_structured_429_before_sse(self):
        client = TestClient(app, client=("198.51.100.10", 50000))
        try:
            for index in range(10):
                response = self._post(client, f"ip-session-{index}")
                self.assertEqual(response.status_code, 200)

            response = self._post(client, "ip-session-blocked")
        finally:
            client.close()

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertGreaterEqual(int(response.headers["Retry-After"]), 1)
        error = response.json()["data"]["error"]
        self.assertEqual(error["code"], "RATE_LIMITED")
        self.assertTrue(error["retryable"])
        self.assertGreaterEqual(error["retry_after_seconds"], 1)

    def test_session_limit_applies_across_client_addresses(self):
        session_id = "shared-session"
        for index in range(30):
            client = TestClient(
                app,
                client=(f"198.51.100.{index + 20}", 50000),
            )
            try:
                response = self._post(client, session_id)
                self.assertEqual(response.status_code, 200)
            finally:
                client.close()

        client = TestClient(app, client=("203.0.113.10", 50000))
        try:
            response = self._post(client, session_id)
        finally:
            client.close()

        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.json()["data"]["error"]["code"],
            "RATE_LIMITED",
        )


if __name__ == "__main__":
    unittest.main()
