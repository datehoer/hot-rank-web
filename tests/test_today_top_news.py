import unittest
import sys
import types
from unittest.mock import patch

config = types.ModuleType("config")
config.REDIS_PASSWORD = ""
config.REDIS_HOST = "localhost"
config.REDIS_PORT = 6379
config.REDIS_DB = 0
config.PG_HOST = "localhost"
config.PG_PORT = 5432
config.PG_USER = "user"
config.PG_PASSWORD = "password"
config.PG_DB = "db"
config.api_url = "https://example.com"
config.api_headers = {}
config.news_sites = ["澎湃新闻"]
config.EMAIL = {
    "user": "test@example.com",
    "host": "smtp.example.com",
    "port": 587,
    "password": "password",
}
sys.modules["config"] = config

import app


class FakeRedis:
    async def get(self, key):
        return None

    async def set(self, *args, **kwargs):
        return True

    async def delete(self, *args, **kwargs):
        return 1

    async def setex(self, *args, **kwargs):
        return True


class TodayTopNewsTest(unittest.IsolatedAsyncioTestCase):
    async def test_empty_model_response_returns_clear_error(self):
        async def fake_get_data(item_id):
            return {
                "code": 200,
                "msg": "success",
                "data": [
                    {
                        "name": "澎湃新闻",
                        "data": [
                            {
                                "hot_label": "A",
                                "hot_url": "https://example.com",
                                "hot_value": "1",
                            }
                        ],
                    }
                ],
            }

        async def fake_chat_with_model(messages, response_format):
            return ""

        with patch.object(app, "redis_client", FakeRedis()), patch.object(
            app, "get_data", fake_get_data
        ), patch.object(app, "chatWithModel", fake_chat_with_model), patch.object(
            app.logging, "error"
        ):
            result = await app.getTodayTopNews()

        self.assertEqual(result["code"], 500)
        self.assertIn("AI response is empty", result["msg"])
        self.assertNotIn("object has no attribute", result["msg"])


if __name__ == "__main__":
    unittest.main()
