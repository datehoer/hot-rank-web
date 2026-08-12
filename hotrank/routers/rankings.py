import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Request

from hotrank.cache import redis_cache
from hotrank.services.rank_data import load_rank_data
from hotrank.services.today_news import generate_today_top_news


router = APIRouter()


@router.get("/holiday")
async def get_holiday():
    holidays = await redis_cache.get("holidays")
    return {"code": 200, "msg": "success", "data": json.loads(holidays)}


@router.get("/refresh")
async def refresh():
    ttl_time_second = await redis_cache.ttl("rank")
    message = {
        "code": 200,
        "msg": "星链回复是最新数据啦",
        "data": [],
    }
    if ttl_time_second:
        current_time = datetime.now()
        total_ttl = timedelta(hours=1)
        creation_time = current_time - (
            total_ttl - timedelta(seconds=ttl_time_second)
        )
        nearest_hour = current_time.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        if creation_time < nearest_hour:
            await redis_cache.delete("rank")
            await redis_cache.delete("todayTopNews")
            message["msg"] = "已通知星链重新链接中"
        else:
            rank_data = await redis_cache.get("rank")
            if rank_data:
                rank_json = json.loads(rank_data)
                time_status = [
                    task_time
                    for task_time in rank_json
                    if datetime.strptime(
                        task_time["insert_time"],
                        "%Y-%m-%d %H:%M:%S",
                    ) < nearest_hour
                ]

                if time_status:
                    await redis_cache.delete("rank")
                    await redis_cache.delete("todayTopNews")
                    message["msg"] = "已通知星链重新链接中"
    return message


@router.get("/todayTopNews")
async def get_today_top_news(request: Request):
    today_top_news_data = await redis_cache.get("todayTopNews")
    if today_top_news_data:
        return {
            "code": 200,
            "msg": "success",
            "data": json.loads(today_top_news_data),
        }

    get_today_top_news_status = await redis_cache.get(
        "today_top_news_task"
    )
    if get_today_top_news_status:
        return {"code": 200, "msg": "success", "data": []}

    await redis_cache.set("today_top_news_task", "1", 1800)
    return await generate_today_top_news(request.app.state.pg_pool)


@router.get("/rank/{item_id}")
async def get_data(item_id: str, request: Request):
    return await load_rank_data(request.app.state.pg_pool, item_id)
