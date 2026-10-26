import ast
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock

import redis

from hotrank.source_catalog import (
    LOCAL_SOURCE_CARDS,
    merge_query_sources,
    merge_source_cards,
    sync_catalog,
)
from hotrank.agent.source_config import SOURCE_LABELS, parse_allowed_query_sources
from hotrank.agent.tool_registry import SUPPORTED_SEARCH_PLATFORMS


class SourceCatalogTest(unittest.TestCase):
    def test_merge_preserves_existing_order_names_and_metadata(self):
        existing = [{"name": "My custom CBC", "tablename": "cbc", "custom": True},
                    {"name": "Existing community", "tablename": "v2ex"}]
        result = merge_source_cards(existing)
        self.assertEqual(result[:2], existing)
        self.assertEqual(len(result), 24)
        self.assertEqual(merge_source_cards(result), result)
        self.assertEqual(len(existing), 2)

    def test_invalid_catalog_is_rejected_without_silently_replacing_it(self):
        for value in [None, {}, [{"name": "Example", "tablename": 'bad";sql'}],
                      [{"name": "", "tablename": "cbc"}]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                merge_source_cards(value)

    def test_new_sources_are_registered_for_agent_queries_and_labels(self):
        keys = [card["tablename"] for card in LOCAL_SOURCE_CARDS]
        self.assertEqual(len(set(keys)), 23)
        self.assertEqual(len(SUPPORTED_SEARCH_PLATFORMS), len(set(SUPPORTED_SEARCH_PLATFORMS)))
        default = parse_allowed_query_sources(None)
        for card in LOCAL_SOURCE_CARDS:
            self.assertIn(card["tablename"], default)
            self.assertEqual(SOURCE_LABELS[card["tablename"]], card["name"])

    def test_query_merge_preserves_implicit_defaults_and_explicit_choices(self):
        self.assertIsNone(merge_query_sources(None))
        merged = merge_query_sources(["v2ex", "cbc"])
        self.assertEqual(merged[:2], ["v2ex", "cbc"])
        self.assertEqual(len(merged), 24)
        self.assertNotIn("weibo_hot_search", merged)
        self.assertEqual(merge_query_sources(merged), merged)
        with self.assertRaises(ValueError):
            merge_query_sources({"cbc": True})

    def test_legacy_bootstrap_also_keeps_the_new_sources(self):
        path = Path(__file__).resolve().parents[1] / "tools" / "pushSomethings.py"
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "table" for target in node.targets
            ):
                cards = ast.literal_eval(node.value)
                break
        else:
            self.fail("Bootstrap card list not found")
        by_key = {card["tablename"]: card for card in cards}
        for card in LOCAL_SOURCE_CARDS:
            self.assertEqual(by_key[card["tablename"]], card)

    def pipeline(self, cards=None, query=None):
        cards = [{"name": "Existing", "tablename": "v2ex"}] if cards is None else cards
        values = {"card_table": json.dumps(cards), "agent:query:sources": json.dumps(query) if query is not None else None}
        client, pipe = MagicMock(), MagicMock()
        client.pipeline.return_value.__enter__.return_value = pipe
        pipe.get.side_effect = values.get
        return client, pipe, values

    def test_preview_and_idempotent_apply_never_write(self):
        client, pipe, _ = self.pipeline()
        plan = sync_catalog(client)
        self.assertEqual(plan["added"], 23)
        self.assertFalse(plan["applied"])
        pipe.set.assert_not_called()
        pipe.delete.assert_not_called()
        pipe.execute.assert_not_called()
        client, pipe, _ = self.pipeline(merge_source_cards([]))
        plan = sync_catalog(client, apply=True)
        self.assertFalse(plan["changed"])
        pipe.execute.assert_not_called()

    def test_apply_backs_up_and_updates_only_the_catalogs_and_rank_cache(self):
        client, pipe, original = self.pipeline(query=["v2ex"])
        result = sync_catalog(client, apply=True)
        self.assertTrue(result["applied"])
        self.assertEqual(result["cards_after"], 24)
        writes = pipe.set.call_args_list
        self.assertEqual(len(writes), 3)
        self.assertEqual(json.loads(writes[0].args[1]), original)
        self.assertEqual(writes[0].kwargs["ex"], 7 * 86400)
        self.assertTrue(writes[1].kwargs["keepttl"])
        self.assertTrue(writes[2].kwargs["keepttl"])
        pipe.delete.assert_called_once_with("rank")
        pipe.execute.assert_called_once()

    def test_concurrent_changes_are_reloaded_before_retrying(self):
        client, pipe, _ = self.pipeline()
        pipe.execute.side_effect = [redis.WatchError(), None]
        result = sync_catalog(client, apply=True)
        self.assertTrue(result["applied"])
        self.assertEqual(pipe.watch.call_count, 2)


if __name__ == "__main__":
    unittest.main()
