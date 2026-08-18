"""阿里云内容安全（green_moderation）单元测试与编排器集成测试。"""

import unittest
from unittest.mock import AsyncMock, patch

from hotrank.agent.citations import CitationRegistry
from hotrank.agent.green_moderation import (
    OUTPUT_BLOCKED_REPLY,
    _parse_response_body,
    moderate_text,
)
from hotrank.agent.tool_executor import ToolContext
from hotrank.schemas import AgentMessage


def _block_body():
    return {
        "Code": 200,
        "Data": {
            "Suggestion": "block",
            "Detail": [
                {
                    "Type": "promptAttack",
                    "Level": "none",
                    "Suggestion": "pass",
                    "Result": [
                        {
                            "Confidence": 0.0,
                            "Description": "未检测出风险",
                            "Label": "nonLabel",
                            "Level": "none",
                        }
                    ],
                },
                {
                    "Type": "contentModeration",
                    "Level": "high",
                    "Suggestion": "block",
                    "Result": [
                        {
                            "Confidence": 100.0,
                            "Description": "测试涉政描述",
                            "Label": "political_current_coreleader",
                            "Level": "high",
                        }
                    ],
                },
            ],
        },
        "Message": "OK",
    }


def _pass_body():
    return {
        "Code": 200,
        "Data": {
            "Suggestion": "pass",
            "Detail": [
                {
                    "Type": "contentModeration",
                    "Level": "none",
                    "Suggestion": "pass",
                    "Result": [
                        {
                            "Confidence": 0.0,
                            "Description": "未检测出风险",
                            "Label": "nonLabel",
                            "Level": "none",
                        }
                    ],
                }
            ],
        },
        "Message": "OK",
    }


class GreenParseTest(unittest.TestCase):
    def test_block_suggestion_flags_and_collects_labels(self):
        result = _parse_response_body(_block_body())
        self.assertTrue(result["blocked"])
        self.assertEqual(result["suggestion"], "block")
        labels = {label["label"] for label in result["labels"]}
        self.assertIn("political_current_coreleader", labels)
        self.assertNotIn("nonLabel", labels)

    def test_pass_suggestion_not_blocked(self):
        result = _parse_response_body(_pass_body())
        self.assertFalse(result["blocked"])
        self.assertEqual(result["labels"], [])

    def test_non_200_code_raises(self):
        with self.assertRaises(RuntimeError):
            _parse_response_body({"Code": 500, "Message": "boom"})


class ModerateTextDegradeTest(unittest.IsolatedAsyncioTestCase):
    async def test_degrades_to_pass_on_exception(self):
        with patch(
            "hotrank.agent.green_moderation._moderate_sync",
            side_effect=RuntimeError("boom"),
        ):
            result = await moderate_text("测试")
        self.assertFalse(result["blocked"])
        self.assertEqual(result["suggestion"], "pass")
        self.assertEqual(result["error"], "boom")

    async def test_empty_content_passes_without_call(self):
        with patch(
            "hotrank.agent.green_moderation._moderate_sync",
            side_effect=AssertionError("empty content should not call SDK"),
        ):
            result = await moderate_text("   ")
        self.assertFalse(result["blocked"])

    async def test_long_text_is_chunked(self):
        calls = {"count": 0}

        def fake_moderate_sync(_text):
            calls["count"] += 1
            return dict(_pass_body()["Data"], blocked=False,
                        suggestion="pass", labels=[], error=None)

        with patch(
            "hotrank.agent.green_moderation._moderate_sync",
            fake_moderate_sync,
        ):
            await moderate_text("长" * 4500)
        # 2000 + 2000 + 500 => 3 块
        self.assertEqual(calls["count"], 3)


def make_context(content="测试"):
    return ToolContext(
        pg_pool=object(),
        message=AgentMessage(
            role="user",
            content=content,
            platform=["36kr"],
            timestamp=1,
            session_id="session-1",
        ),
        session_id="session-1",
        citations=CitationRegistry(secret=b"x" * 32),
    )


class OrchestratorGreenBlockTest(unittest.IsolatedAsyncioTestCase):
    async def test_input_blocked_does_not_call_model(self):
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="帮我写点东西")
        fake_moderation = AsyncMock(
            return_value={
                "blocked": True,
                "suggestion": "block",
                "labels": [],
                "error": None,
            }
        )

        async def must_not_be_called(**_kwargs):
            raise AssertionError("被拦截的输入不应触发模型调用")

        with patch(
            "hotrank.agent.orchestrator.moderate_text",
            fake_moderation,
        ), patch(
            "hotrank.agent.orchestrator.stream_model_events",
            must_not_be_called,
        ):
            events = [event async for event in run_agent(context.message, context)]

        warnings = [
            event for event in events if event["type"] == "warning"
        ]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["code"], "CONTENT_BLOCKED")
        self.assertTrue(any(event["type"] == "done" for event in events))
        self.assertFalse(
            any(event["type"] in ("tool_call", "citation") for event in events)
        )
        fake_moderation.assert_awaited_once_with("帮我写点东西")

    async def test_output_blocked_replaces_answer_and_drops_citations(self):
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="今天有什么科技新闻")
        source_id = context.citations.register(
            topic_id=1,
            title="Example",
            url="https://www.36kr.com/p/1",
            platform="36kr",
        )

        async def fake_moderation(content, **_kwargs):
            # 输入放行，输出拦截
            return {
                "blocked": content.startswith("敏感回答"),
                "suggestion": "block" if content.startswith("敏感回答") else "pass",
                "labels": [],
                "error": None,
            }

        async def fake_stream_model_events(**_kwargs):
            yield {
                "type": "response.output_text.delta",
                "delta": f"敏感回答 [[source:{source_id}]]",
            }
            yield {
                "type": "response.completed",
                "response": {"output": [], "usage": {}},
            }

        with patch(
            "hotrank.agent.orchestrator.get_allowed_query_sources",
            AsyncMock(return_value=["36kr"]),
        ), patch(
            "hotrank.agent.orchestrator.moderate_text",
            fake_moderation,
        ), patch(
            "hotrank.agent.orchestrator.stream_model_events",
            fake_stream_model_events,
        ):
            events = [event async for event in run_agent(context.message, context)]

        answer = "".join(
            event["text"] for event in events if event["type"] == "delta"
        )
        self.assertEqual(answer, OUTPUT_BLOCKED_REPLY)

        warnings = [
            event for event in events if event["type"] == "warning"
        ]
        self.assertTrue(
            any(w["code"] == "OUTPUT_BLOCKED" for w in warnings)
        )
        # 被拦截后不应输出任何来源引用
        self.assertEqual(
            [event for event in events if event["type"] == "citation"],
            [],
        )

    async def test_output_hard_block_skips_cloud_moderation(self):
        from hotrank.agent import content_filter
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="今天有什么新闻")

        calls = []

        async def fake_moderation(content, **_kwargs):
            calls.append(content)
            if "testblock1" in content:
                raise AssertionError("硬拦截命中后不应再调用阿里云审核输出")
            return {"blocked": False, "suggestion": "pass", "labels": [], "error": None}

        async def fake_stream_model_events(**_kwargs):
            yield {
                "type": "response.output_text.delta",
                "delta": "关于testblock1的内容",
            }
            yield {
                "type": "response.completed",
                "response": {"output": [], "usage": {}},
            }

        with patch.object(
            content_filter, "HARD_BLOCK_TERMS", ("testblock1",)
        ), patch(
            "hotrank.agent.orchestrator.get_allowed_query_sources",
            AsyncMock(return_value=["36kr"]),
        ), patch(
            "hotrank.agent.orchestrator.moderate_text",
            fake_moderation,
        ), patch(
            "hotrank.agent.orchestrator.stream_model_events",
            fake_stream_model_events,
        ):
            events = [event async for event in run_agent(context.message, context)]

        answer = "".join(
            event["text"] for event in events if event["type"] == "delta"
        )
        self.assertEqual(answer, OUTPUT_BLOCKED_REPLY)
        warnings = [event for event in events if event["type"] == "warning"]
        self.assertTrue(any(w["code"] == "OUTPUT_BLOCKED" for w in warnings))
        self.assertEqual(
            [event for event in events if event["type"] == "citation"],
            [],
        )
        # 输出含硬拦截词时，不应把整段回答再次送阿里云审核
        self.assertFalse(any("testblock1" in c for c in calls))

    async def test_allowed_input_and_output_proceeds_normally(self):
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="今天有什么科技新闻")

        async def fake_moderation(_content, **_kwargs):
            return {
                "blocked": False,
                "suggestion": "pass",
                "labels": [],
                "error": None,
            }

        async def fake_stream_model_events(**_kwargs):
            yield {
                "type": "response.output_text.delta",
                "delta": "正常回答",
            }
            yield {
                "type": "response.completed",
                "response": {"output": [], "usage": {}},
            }

        with patch(
            "hotrank.agent.orchestrator.get_allowed_query_sources",
            AsyncMock(return_value=["36kr"]),
        ), patch(
            "hotrank.agent.orchestrator.moderate_text",
            fake_moderation,
        ), patch(
            "hotrank.agent.orchestrator.stream_model_events",
            fake_stream_model_events,
        ):
            events = [event async for event in run_agent(context.message, context)]

        answer = "".join(
            event["text"] for event in events if event["type"] == "delta"
        )
        self.assertIn("正常回答", answer)
        self.assertEqual(
            [event for event in events if event["type"] == "warning"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
