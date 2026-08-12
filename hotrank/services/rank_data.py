import json
import logging
import time
import traceback

from fastapi import HTTPException

from common import (
    parse_acfun,
    parse_anquanke,
    parse_bilibili_hot,
    parse_common,
    parse_coolan,
    parse_csdn,
    parse_douban,
    parse_douyin_hot,
    parse_hupu,
    parse_juejin_hot,
    parse_linuxdo,
    parse_mcpmarket,
    parse_openeye,
    parse_pengpai,
    parse_pmcaff,
    parse_shaoshupai_hot,
    parse_tencent_news,
    parse_tieba_topic,
    parse_toutiao_hot,
    parse_wallstreetcn,
    parse_weibo_hot_search,
    parse_woshipm,
    parse_wx_read_rank,
    parse_xueqiu,
    parse_yiche,
    parse_youshedubao,
    parse_youxiputao,
    parse_zhanku,
    parse_zhihu_hot_list,
    parse_zongheng,
)
from hotrank.cache import redis_cache
from hotrank.services.rss import generate_rank_rss


PARSER_REGISTRY = {
    "zhihu_hot_list": parse_zhihu_hot_list,
    "mcpmarket": parse_mcpmarket,
    "weibo_hot_search": parse_weibo_hot_search,
    "bilibili_hot": parse_bilibili_hot,
    "douyin_hot": parse_douyin_hot,
    "juejin_hot": parse_juejin_hot,
    "shaoshupai_hot": parse_shaoshupai_hot,
    "tieba_topic": parse_tieba_topic,
    "toutiao_hot": parse_toutiao_hot,
    "wx_read_rank": parse_wx_read_rank,
    "acfun": parse_acfun,
    "anquanke": parse_anquanke,
    "csdn": parse_csdn,
    "openeye": parse_openeye,
    "pmcaff": parse_pmcaff,
    "tencent_news": parse_tencent_news,
    "woshipm": parse_woshipm,
    "xueqiu": parse_xueqiu,
    "yiche": parse_yiche,
    "youshedubao": parse_youshedubao,
    "youxiputao": parse_youxiputao,
    "zhanku": parse_zhanku,
    "zongheng": parse_zongheng,
    "hupu": parse_hupu,
    "wallstreetcn": parse_wallstreetcn,
    "coolan": parse_coolan,
    "pengpai": parse_pengpai,
    "linuxdo": parse_linuxdo,
}


async def load_rank_data(pg_pool, item_id: str):
    if item_id != "hot":
        return {"error": "Invalid value"}

    cache_key = "rank"
    try:
        cached_data = await redis_cache.get(cache_key)
        if cached_data:
            return {
                "code": 200,
                "msg": "success",
                "data": json.loads(cached_data),
            }
    except Exception as exc:
        logging.error(f"Redis error: {exc}")

    try:
        data = []
        try:
            blog_data = await redis_cache.get("myblog")
            if blog_data:
                data.append(json.loads(blog_data))
        except Exception as exc:
            logging.error(f"Redis get error: {exc}")

        table_dict = json.loads(await redis_cache.get("card_table"))
        async with pg_pool.acquire() as conn:
            for item in table_dict:
                collection_name = item["tablename"]
                if collection_name in ["myblog"]:
                    continue
                try:
                    query = (
                        f'SELECT * FROM "{collection_name}" '
                        "WHERE insert_time IS NOT NULL "
                        "ORDER BY insert_time DESC LIMIT 1"
                    )
                    latest_record = await conn.fetchrow(query)
                    if not latest_record:
                        continue

                    insert_time = latest_record["insert_time"]
                    latest_record = {
                        "data": json.loads(dict(latest_record)["data"])
                    }
                    if collection_name == "douban_movie":
                        koubei, beimei = parse_douban(latest_record)
                        local_time = time.localtime(insert_time)
                        data.append(
                            {
                                "name": "豆瓣电影一周口碑榜",
                                "data": koubei,
                                "insert_time": time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    local_time,
                                ),
                                "id": 998,
                            }
                        )
                        data.append(
                            {
                                "name": "豆瓣电影北美票房榜",
                                "data": beimei,
                                "insert_time": time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    local_time,
                                ),
                                "id": 999,
                            }
                        )
                        continue

                    parser = PARSER_REGISTRY.get(collection_name, parse_common)
                    latest_record = parser(latest_record)
                    local_time = time.localtime(insert_time)
                    data.append(
                        {
                            "name": item["name"],
                            "data": latest_record,
                            "insert_time": time.strftime(
                                "%Y-%m-%d %H:%M:%S",
                                local_time,
                            ),
                        }
                    )
                except Exception as exc:
                    logging.error(f"Error parsing {collection_name}: {exc}")
                    logging.error(traceback.format_exc())

        try:
            await redis_cache.setex(
                cache_key,
                3600,
                json.dumps(data, ensure_ascii=False),
            )
        except Exception as exc:
            logging.error(f"Redis setex error: {exc}")

        generate_rank_rss(data)
        return {
            "code": 200,
            "msg": "success",
            "data": data,
        }
    except Exception as exc:
        logging.error(f"Postgresql error: {exc}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        ) from exc
