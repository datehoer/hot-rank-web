"""Local publisher cards and an idempotent rollout into the existing Redis catalog.

Preview: python -m hotrank.source_catalog
Apply:   python -m hotrank.source_catalog --apply
Run in the API environment so credentials come from its managed config.py.
"""
import argparse
from datetime import datetime, timezone
import json
import re
from uuid import uuid4

LOCAL_SOURCE_CARDS = [
    {"name": "CBC（加拿大新闻）", "tablename":"cbc"},
    {"name": "Global News（加拿大最新）", "tablename":"globalnews"},
    {"name": "CTV News（加拿大最新）", "tablename":"ctv"},
    {"name": "National Post（加拿大最新）", "tablename":"nationalpost"},
    {"name": "Radio-Canada（加拿大法语要闻）", "tablename":"radiocanada"},
    {"name": "SPIEGEL（德国头条）", "tablename":"spiegel"},
    {"name": "ZEIT（德国最新）", "tablename":"zeit"},
    {"name": "heise（德国科技最新）", "tablename":"heise"},
    {"name": "Süddeutsche（德国要闻）", "tablename":"sueddeutsche"},
    {"name": "mydealz（德国社区优惠）", "tablename":"mydealz"},
    {"name": "Naver（韩国各媒体热读）", "tablename":"naver_news"},
    {"name": "NEWSIS（韩国热读）", "tablename":"newsis"},
    {"name": "Bizwatch（韩国财经热读）", "tablename":"bizwatch"},
    {"name": "DC Inside（韩国实时精选）", "tablename":"dcinside"},
    {"name": "Nate Pann（韩国热帖）", "tablename":"nate_pann"},
    {"name": "ABC（澳大利亚头条）", "tablename":"abc_au"},
    {"name": "SBS（澳大利亚头条）", "tablename":"sbs_au"},
    {"name": "OzBargain（澳大利亚社区优惠）", "tablename":"ozbargain"},
    {"name": "Stuff（新西兰最新）", "tablename":"stuff"},
    {"name": "NZ Herald（新西兰新闻）", "tablename":"nzherald"},
    {"name": "1News（新西兰头条）", "tablename":"tvnz"},
    {"name": "Cheapies（新西兰社区优惠）", "tablename":"cheapies"},
    {"name": "Geekzone（新西兰最新讨论）", "tablename":"geekzone"},
]


def merge_source_cards(existing, additions=LOCAL_SOURCE_CARDS):
    """Append missing sources while preserving current names, metadata and order."""
    for cards in (existing, additions):
        if not isinstance(cards, list):
            raise ValueError("Source cards must be a list")
        for card in cards:
            if (not isinstance(card, dict)
                    or not isinstance(card.get("name"), str) or not card["name"].strip()
                    or not isinstance(card.get("tablename"), str)
                    or not re.fullmatch(r"[a-z0-9_]+", card["tablename"])):
                raise ValueError("Invalid source card")
    merged = [dict(card) for card in existing]
    seen = {card["tablename"] for card in existing}
    for card in additions:
        if card["tablename"] not in seen:
            merged.append(dict(card))
            seen.add(card["tablename"])
    return merged


def merge_query_sources(existing):
    """Keep the default registry implicit; extend an explicit allowlist in order."""
    if existing is None:
        return None
    if not isinstance(existing, list) or not all(isinstance(key, str) for key in existing):
        raise ValueError("Query sources must be a string list")
    return list(dict.fromkeys([*existing, *(card["tablename"] for card in LOCAL_SOURCE_CARDS)]))


def sync_catalog(client, *, apply=False):
    """Watch both registries so concurrent changes cannot be overwritten."""
    import redis

    for _ in range(3):
        with client.pipeline() as pipe:
            try:
                pipe.watch("card_table", "agent:query:sources")
                raw_cards = pipe.get("card_table")
                raw_query = pipe.get("agent:query:sources")
                if raw_cards is None:
                    raise ValueError("The existing card catalog is missing; initialize it first")
                cards = json.loads(raw_cards)
                query = json.loads(raw_query) if raw_query is not None else None
                merged = merge_source_cards(cards)
                merged_query = merge_query_sources(query)
                changed = merged != cards or merged_query != query
                result = {"cards_before": len(cards), "cards_after": len(merged),
                          "added": len(merged) - len(cards), "changed": changed, "applied": False}
                if not apply or not changed:
                    return result
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup_key = f"release:source-catalog:{stamp}:{uuid4().hex[:8]}"
                pipe.multi()
                pipe.set(backup_key, json.dumps({"card_table": raw_cards,
                                                "agent:query:sources": raw_query}),
                         ex=7 * 86400)
                pipe.set("card_table", json.dumps(merged, ensure_ascii=False), keepttl=True)
                if merged_query != query:
                    pipe.set("agent:query:sources", json.dumps(merged_query), keepttl=True)
                pipe.delete("rank")
                pipe.execute()
                return {**result, "applied": True, "backup_key": backup_key}
            except redis.WatchError:
                continue
    raise RuntimeError("Source catalog changed concurrently; no update was applied")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Merge the new sources and invalidate rank")
    args = parser.parse_args()
    import redis
    from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD,
                         decode_responses=True, socket_timeout=5, socket_connect_timeout=5)
    try:
        print(json.dumps(sync_catalog(client, apply=args.apply), ensure_ascii=False))
    finally:
        client.close()


if __name__ == "__main__":
    main()
