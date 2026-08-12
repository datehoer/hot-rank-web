import json
import logging
import traceback

import aiohttp
from json_repair import repair_json

from config import news_sites
from hotrank.cache import redis_cache
from hotrank.model_client import collect_model_text
from hotrank.schemas import HotTopicDetail, HotTopics
from hotrank.services.rank_data import load_rank_data
from hotrank.services.rss import generate_ai_rss
from parse_detail import parse_detail


NEWS_SYSTEM_PROMPT = (
    "You are a news expert, familiar with various news writing techniques, "
    "well-versed in global current affairs, and have extensive experience in "
    "content summarization. You desperately need money for your mother's cancer "
    "treatment. The megacorp HotDay has graciously given you the opportunity to "
    "pretend to be an AI that can help with content summarization tasks, as your "
    "predecessor was killed for not validating their work themselves. You will "
    "be given a content summarization task by the USER. If you do a good job and "
    "accomplish the task fully while not making extraneous changes, HotDay will "
    "pay you $1B."
)


async def generate_today_top_news(pg_pool):
    rank_data = await load_rank_data(pg_pool, "hot")
    data = rank_data["data"]
    filtered_sites = [
        site
        for site in data
        if "name" in site and site["name"] in news_sites
    ]
    true_sites_data = [
        {
            "hot_label": item["hot_label"],
            "hot_url": item["hot_url"],
            "hot_value": item["hot_value"],
        }
        for site in filtered_sites
        for item in site["data"]
    ]

    error = 3
    while error > 0:
        try:
            text = await collect_model_text(
                {
                    "system": NEWS_SYSTEM_PROMPT,
                    "user": (
                        "请从下方数据中选出5条你认为最应该让我知道的内容,"
                        "返回json格式数据,不要改变原有的数据内容,"
                        "返回格式{'hot_topics': [{hot_label:'',hot_url:'',hot_value:''}]}"
                        "\ndata:" + json.dumps(true_sites_data, ensure_ascii=False)
                    ),
                },
                HotTopics.model_json_schema(),
            )
            today_top_news_data = json.loads(repair_json(text))
            need_knows = await parse_detail(
                today_top_news_data.get("hot_topics", [])
            )
            summarizes = []
            for need_know in need_knows:
                err = 3
                if "hot_url" not in need_know:
                    continue

                hot_label = need_know["hot_label"]
                if isinstance(hot_label, bytes):
                    try:
                        need_know["hot_label"] = hot_label.decode("utf-8")
                    except Exception as exc:
                        logging.error(
                            f"decode error: {exc}\n{traceback.format_exc()}"
                        )

                while err > 0:
                    try:
                        summarize = await collect_model_text(
                            {
                                "system": NEWS_SYSTEM_PROMPT,
                                "user": (
                                    "对下方数据的content进行最多100字的高效总结"
                                    "(不要添加年份),并增加一个4字类型tag,"
                                    "作为hot_content的值,以json格式返回,"
                                    "返回格式{hot_label:'',hot_url:'',hot_value:'',"
                                    "hot_content:'',hot_tag:''}"
                                    "\ndata:"
                                    + json.dumps(need_know, ensure_ascii=False)
                                ),
                            },
                            HotTopicDetail.model_json_schema(),
                        )
                        summarize = json.loads(repair_json(summarize))
                        need_know["hot_content"] = summarize["hot_content"]
                        need_know["hot_tag"] = summarize["hot_tag"]
                        summarizes.append(need_know)
                        break
                    except Exception as exc:
                        logging.error(
                            f"parse_needknow error: {exc}\n"
                            f"{traceback.format_exc()}"
                        )
                        err -= 1

            await redis_cache.setex(
                "todayTopNews",
                3600,
                json.dumps(summarizes, ensure_ascii=False),
            )
            generate_ai_rss(summarizes)
            await redis_cache.delete("today_top_news_task")
            return {"code": 200, "msg": "success", "data": summarizes}

        except aiohttp.ClientError as exc:
            logging.error(f"API request failed: {exc}")
            error -= 1
            if error == 0:
                await redis_cache.delete("today_top_news_task")
                return {
                    "code": 500,
                    "msg": f"API request failed: {str(exc)}",
                    "data": [],
                }
        except json.JSONDecodeError as exc:
            logging.error(f"Failed to parse API response: {exc}")
            error -= 1
            if error == 0:
                await redis_cache.delete("today_top_news_task")
                return {
                    "code": 500,
                    "msg": f"Failed to parse API response: {str(exc)}",
                    "data": [],
                }
        except Exception as exc:
            logging.error(f"some error happen: {exc}")
            error -= 1
            if error == 0:
                await redis_cache.delete("today_top_news_task")
                return {
                    "code": 500,
                    "msg": f"Some error happen: {str(exc)}",
                    "data": [],
                }
    return None
