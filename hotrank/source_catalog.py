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
    {"name": "CBC", "tablename":"cbc"},
    {"name": "Global News", "tablename":"globalnews"},
    {"name": "CTV News", "tablename":"ctv"},
    {"name": "National Post", "tablename":"nationalpost"},
    {"name": "Radio-Canada", "tablename":"radiocanada"},
    {"name": "SPIEGEL", "tablename":"spiegel"},
    {"name": "ZEIT", "tablename":"zeit"},
    {"name": "heise", "tablename":"heise"},
    {"name": "Süddeutsche", "tablename":"sueddeutsche"},
    {"name": "mydealz", "tablename":"mydealz"},
    {"name": "Naver", "tablename":"naver_news"},
    {"name": "NEWSIS", "tablename":"newsis"},
    {"name": "Bizwatch", "tablename":"bizwatch"},
    {"name": "DC Inside", "tablename":"dcinside"},
    {"name": "Nate Pann", "tablename":"nate_pann"},
    {"name": "ABC", "tablename":"abc_au"},
    {"name": "SBS", "tablename":"sbs_au"},
    {"name": "OzBargain", "tablename":"ozbargain"},
    {"name": "Stuff", "tablename":"stuff"},
    {"name": "NZ Herald", "tablename":"nzherald"},
    {"name": "1News", "tablename":"tvnz"},
    {"name": "Cheapies", "tablename":"cheapies"},
    {"name": "Geekzone", "tablename":"geekzone"},
]


def merge_source_cards(existing, additions=LOCAL_SOURCE_CARDS):
    """Append sources and remove generated label suffixes, retaining custom names."""
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
    names = {card["tablename"]: card["name"] for card in additions}
    for card in merged:
        name = names.get(card["tablename"])
        if name and re.fullmatch(
            re.escape(name) + r"（(?:加拿大|德国|韩国|澳大利亚|新西兰)[^（）]*）", card["name"]
        ):
            card["name"] = name
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
                          "added": len(merged) - len(cards),
                          "renamed": sum(old["name"] != new["name"] for old, new in zip(cards, merged)),
                          "changed": changed, "applied": False}
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
