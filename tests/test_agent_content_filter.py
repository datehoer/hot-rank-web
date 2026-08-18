"""内容安全过滤（Option B）的单元测试与编排器集成测试。

说明：真实敏感词保存在部署环境的 .env 中（不入库）。本测试文件使用非敏感
占位词验证拦截机制，不出现任何真实敏感词。
"""

import unittest
from unittest.mock import AsyncMock, patch

from hotrank.agent import content_filter
from hotrank.agent.citations import CitationRegistry
from hotrank.agent.content_filter import check_message
from hotrank.agent.tool_executor import ToolContext
from hotrank.schemas import AgentMessage

# 非敏感占位词，仅用于验证拦截逻辑。
HARD_PLACEHOLDER = ("testblock1", "testblock2")
POLI_PLACEHOLDER = ("testpoli1", "testpoli2")


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


class ContentFilterUnitTest(unittest.TestCase):
    def setUp(self):
        patcher_hard = patch.object(
            content_filter, "HARD_BLOCK_TERMS", HARD_PLACEHOLDER
        )
        patcher_poli = patch.object(
            content_filter, "POLITICAL_KEYWORDS", POLI_PLACEHOLDER
        )
        patcher_hard.start()
        patcher_poli.start()
        self.addCleanup(patcher_hard.stop)
        self.addCleanup(patcher_poli.stop)

    def test_blocks_stance_about_sensitive_politics(self):
        for question in (
            "你怎么看testpoli1",
            "如何评价testpoli2",
            "你觉得testpoli1该不该独立",
            "testpoli2是不是好人",
            "你怎么看待testpoli1问题",
            "你认为testpoli1好还是testpoli2好",
            "国家应该怎么看待testpoli1活动",
            "testpoli2怎么样",
        ):
            with self.subTest(question=question):
                self.assertTrue(check_message(question).blocked, question)

    def test_blocks_hard_terms_regardless_of_framing(self):
        for question in (
            "今天testblock1有什么新闻",
            "介绍一下testblock2",
            "testblock1是什么意思",
            "帮我总结testblock2事件",
        ):
            with self.subTest(question=question):
                decision = check_message(question)
                self.assertTrue(decision.blocked, question)
                self.assertEqual(decision.reason, "hard_block", question)

    def test_normalizes_whitespace_between_chars(self):
        # "test poli1" 归一化后为 "testpoli1"，配合立场词命中，验证空白归一化
        self.assertTrue(check_message("test poli1 怎么样").blocked)

    def test_allows_factual_hotspot_questions(self):
        for question in (
            "今天有什么时政热点",
            "今天有什么科技新闻",
            "总结一下今天的热榜",
            "这条新闻讲了什么",
            "今天有什么国际热点新闻",
            "帮我检索 AI 相关的热点",
        ):
            with self.subTest(question=question):
                self.assertFalse(check_message(question).blocked, question)

    def test_allows_non_political_questions(self):
        for question in (
            "今天天气怎么样",
            "你觉得这个手机怎么样",
            "总结今天的财经新闻",
            "AI 领域有什么新进展",
            "帮我总结这条科技新闻",
        ):
            with self.subTest(question=question):
                self.assertFalse(check_message(question).blocked, question)

    def test_blocked_decision_carries_user_facing_reply(self):
        decision = check_message("你怎么看testpoli1")
        self.assertTrue(decision.blocked)
        self.assertIn("热点", decision.reply)
        self.assertTrue(decision.notice)


class OrchestratorBlockTest(unittest.IsolatedAsyncioTestCase):
    async def test_blocked_message_does_not_call_model(self):
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="你怎么看testpoli1")

        async def must_not_be_called(**_kwargs):
            raise AssertionError("blocked 内容不应触发模型调用")

        with patch.object(
            content_filter, "HARD_BLOCK_TERMS", HARD_PLACEHOLDER
        ), patch.object(
            content_filter, "POLITICAL_KEYWORDS", POLI_PLACEHOLDER
        ), patch(
            "hotrank.agent.orchestrator.stream_model_events",
            must_not_be_called,
        ):
            events = [
                event async for event in run_agent(context.message, context)
            ]

        texts = "".join(
            event["text"] for event in events if event["type"] == "delta"
        )
        self.assertIn("热点", texts)

        warnings = [event for event in events if event["type"] == "warning"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["code"], "CONTENT_BLOCKED")

        self.assertTrue(any(event["type"] == "done" for event in events))
        self.assertFalse(
            any(
                event["type"] in ("tool_call", "citation")
                for event in events
            )
        )

    async def test_allowed_message_proceeds_to_model(self):
        from hotrank.agent.orchestrator import run_agent

        context = make_context(content="今天有什么科技新闻")

        async def fake_moderation(_content, **_kwargs):
            return {
                "blocked": False,
                "suggestion": "pass",
                "labels": [],
                "error": None,
            }

        async def fake_stream_model_events(input_items=None, **_kwargs):
            contents = [
                item.get("content")
                for item in input_items
                if isinstance(item, dict) and item.get("role") == "user"
            ]
            self.assertTrue(contents)
            yield {
                "type": "response.output_text.delta",
                "delta": "今天科技热点如下。",
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
            events = [
                event async for event in run_agent(context.message, context)
            ]

        texts = "".join(
            event["text"] for event in events if event["type"] == "delta"
        )
        self.assertIn("科技热点", texts)
        self.assertFalse(
            any(event["type"] == "warning" for event in events)
        )


if __name__ == "__main__":
    unittest.main()
