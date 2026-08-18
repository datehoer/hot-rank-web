import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app import app
from hotrank.infrastructure import limiter


class AgentApiValidationTest(unittest.TestCase):
    def setUp(self):
        # 不进入 lifespan，因此不会连接 PostgreSQL。
        self._limiter_enabled = limiter.enabled
        limiter.enabled = False
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        limiter.enabled = self._limiter_enabled

    def _message(self, **overrides):
        payload = {
            "role": "user",
            "content": "hello",
            "platform": ["36kr"],
            "timestamp": 1,
            "session_id": "session-1",
        }
        payload.update(overrides)
        return payload

    def _post(self, payload, allowed=("36kr",)):
        with patch(
            "hotrank.routers.agent.get_allowed_query_sources",
            AsyncMock(return_value=list(allowed)),
        ):
            return self.client.post(
                "/agent/sessions/session-1/message",
                json=payload,
                headers={"Accept": "text/event-stream"},
            )

    def test_session_mismatch_returns_400(self):
        response = self._post(self._message(session_id="other"))
        self.assertEqual(response.status_code, 400)

    def test_invalid_platform_returns_422(self):
        response = self._post(self._message(platform=["__evil__"]))
        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        self.assertEqual(detail["code"], "QUERY_SOURCE_NOT_ALLOWED")
        self.assertEqual(detail["invalid_sources"], ["__evil__"])

    def test_valid_but_disabled_platform_returns_422(self):
        response = self._post(self._message(platform=["ithome"]), allowed=("36kr",))
        self.assertEqual(response.status_code, 422)

    def test_oversized_content_returns_422(self):
        response = self._post(self._message(content="x" * 5000))
        self.assertEqual(response.status_code, 422)

    def test_blank_content_returns_422(self):
        response = self._post(self._message(content="   "))
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
