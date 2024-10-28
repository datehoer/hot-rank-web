from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
import json
import traceback
from config import *
import time
from fastapi.middleware.cors import CORSMiddleware
from common import parse_zhihu_hot_list, parse_weibo_hot_search, parse_bilibili_hot, parse_douyin_hot, parse_juejin_hot, parse_shaoshupai_hot, parse_tieba_topic, parse_toutiao_hot, parse_wx_read_rank
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# MongoDB 设置
mongo_client = AsyncIOMotorClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB_NAME]
table_dict = [
    {"name": "B站热搜", "tablename": "bilibili_hot"},
    {"name": "抖音热搜", "tablename": "douyin_hot"},
    {"name": "掘金热搜", "tablename": "juejin_hot"},
    {"name": "少数派热搜", "tablename": "shaoshupai_hot"},
    {"name": "贴吧热议", "tablename": "tieba_topic"},
    {"name": "头条热搜", "tablename": "toutiao_hot"},
    {"name": "微博热搜", "tablename": "weibo_hot_search"},
    {"name": "微信阅读排行榜", "tablename": "wx_read_rank"},
    {"name": "知乎热榜", "tablename": "zhihu_hot_list"}
]
backoff = ExponentialBackoff(cap=2, base=2)
retry = Retry(backoff=backoff, retries=10)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    retry=retry,
    socket_timeout=10
)

@app.get("/rankCopyWriting")
async def get_copywriting():
    data = await redis_client.srandmember("copywriting")
    return {"code": 200, "msg": "success", "data": data}
@app.get("/yellowCalendar")
async def get_copywriting():
    data = await redis_client.get("yellowCalendar")
    return {"code": 200, "msg": "success", "data": json.loads(data)}
@app.get("/rank/{item_id}")
async def get_data(item_id: str):
    if item_id != "hot":
        return {"error": "Invalid value"}
    cache_key = f"rank"
    
    try:
        # 尝试从 Redis 获取数据
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return {
                "code": 200,
                "msg": "success",
                "data": json.loads(cached_data)
            }
    except Exception as e:
        # 记录日志或处理 Redis 错误
        print(f"Redis error: {e}")

    try:
        data = []
        for item in table_dict:
            try:
                collection_name = item["tablename"]
                collection = mongo_db[collection_name]

                # 查询最新的记录（按 insert_time 降序排序，限制结果为1条）
                cursor = collection.find({"insert_time": {"$ne": None}}).sort("insert_time", -1).limit(1)
                latest_record = await cursor.to_list(length=1)
                latest_record = latest_record[0] if latest_record else None
                if not latest_record:
                    continue
                insert_time = latest_record["insert_time"]
                if collection_name == "zhihu_hot_list":
                    latest_record = parse_zhihu_hot_list(latest_record)
                elif collection_name == "weibo_hot_search":
                    latest_record = parse_weibo_hot_search(latest_record)
                elif collection_name == "bilibili_hot":
                    latest_record = parse_bilibili_hot(latest_record)
                elif collection_name == "douyin_hot":
                    latest_record = parse_douyin_hot(latest_record)
                elif collection_name == "juejin_hot":
                    latest_record = parse_juejin_hot(latest_record)
                elif collection_name == "shaoshupai_hot":
                    latest_record = parse_shaoshupai_hot(latest_record)
                elif collection_name == "tieba_topic":
                    latest_record = parse_tieba_topic(latest_record)
                elif collection_name == "toutiao_hot":
                    latest_record = parse_toutiao_hot(latest_record)
                elif collection_name == "wx_read_rank":
                    latest_record = parse_wx_read_rank(latest_record)
                local_time = time.localtime(insert_time)
                data.append({
                    "name": item["name"],
                    "data": latest_record,
                    "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                })
            except Exception as e:
                print(f"Error parsing {collection_name}: {e}")
                print(traceback.format_exc())
        try:
            # 将数据缓存到 Redis，有效期 60 分钟
            await redis_client.setex(cache_key, 3600, json.dumps(data))
        except Exception as e:
            # 记录日志或处理 Redis 错误
            print(f"Redis setex error: {e}")

        return {
            "code": 200,
            "msg": "success",
            "data": data
        }
    except Exception as e:
        # 处理 MongoDB 错误或其他错误
        print(f"MongoDB error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)