import unittest
from unittest.mock import AsyncMock, patch

from hotrank.services import today_news


class FakeRedis:
    async def get(self, key):
        return None

    async def set(self, *args, **kwargs):
        return True

    async def delete(self, *args, **kwargs):
        return 1

    async def setex(self, *args, **kwargs):
        return True


class ParseHotTopicsResponseTest(unittest.TestCase):
    def test_empty_response_raises(self):
        with self.assertRaisesRegex(ValueError, "AI response is empty"):
            today_news.parse_hot_topics_response("")

    def test_invalid_shape_raises(self):
        with self.assertRaisesRegex(ValueError, "expected object"):
            today_news.parse_hot_topics_response("[]")

    def test_missing_list_raises(self):
        with self.assertRaisesRegex(ValueError, "hot_topics must be a list"):
            today_news.parse_hot_topics_response('{"hot_topics": {}}')

    def test_valid_topics(self):
        topics = today_news.parse_hot_topics_response(
            '{"hot_topics": [{"hot_label": "A", "hot_url": "https://x", "hot_value": "1"}]}'
        )
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0]["hot_label"], "A")


class TodayTopNewsTest(unittest.IsolatedAsyncioTestCase):
    async def test_empty_model_response_returns_clear_error(self):
        fake_rank = {
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

        with patch.object(
            today_news, "load_rank_data", AsyncMock(return_value=fake_rank)
        ), patch.object(
            today_news, "chat_with_model", side_effect=fake_chat_with_model
        ), patch.object(
            today_news, "redis_client", FakeRedis()
        ), patch.object(
            today_news.logging, "error"
        ):
            result = await today_news.generate_today_top_news(None)

        self.assertEqual(result["code"], 500)
        self.assertIn("AI response is empty", result["msg"])
        self.assertNotIn("object has no attribute", result["msg"])


if __name__ == "__main__":
    unittest.main()
