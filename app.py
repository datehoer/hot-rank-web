from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.asyncio import ConnectionPool
import json
import traceback
from config import *
import time
from fastapi.middleware.cors import CORSMiddleware
from sendEmail import send_email
from common import *
from pydantic import BaseModel
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
backoff = ExponentialBackoff(cap=2, base=2)
retry = Retry(backoff=backoff, retries=10)
# 创建连接池
redis_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    retry=retry,
    socket_timeout=60,
    socket_connect_timeout=60,
    socket_keepalive=True,
    health_check_interval=60,
    max_connections=10
)
# 使用连接池创建客户端
redis_client = redis.Redis(connection_pool=redis_pool)
class Feedback(BaseModel):
    subject: str
    content: str
    username: str
@app.get("/rankCopyWriting")
async def get_copywriting():
    data = await redis_client.srandmember("copywriting")
    return {"code": 200, "msg": "success", "data": data}
@app.get("/yellowCalendar")
async def get_copywriting():
    data = await redis_client.get("yellowCalendar")
    return {"code": 200, "msg": "success", "data": json.loads(data)}
@app.get("/music")
async def get_music():
    data = await redis_client.get("music")
    return {"code": 200, "msg": "success", "data": json.loads(data)}
@app.get("/avatar")
async def get_avatar():
    data = await redis_client.srandmember("avatar")
    return {"code": 200, "msg": "success", "data": data}
@app.get("/username")
async def get_username():
    data = await redis_client.srandmember("username")
    return {"code": 200, "msg": "success", "data": data}
@app.post("/feedback")
async def post_feedback(feedback: Feedback):
    send_email(feedback.subject, feedback.content, ["datehoer@gmail.com"])
    return {"code": 200, "msg": "success"}
@app.get("/get_cards")
async def get_cards():
    data = await redis_client.get("card_table")
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
        table_dict = json.loads(await redis_client.get("card_table"))
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
                elif collection_name == "acfun":
                    latest_record = parse_acfun(latest_record)
                elif collection_name == "anquanke":
                    latest_record = parse_anquanke(latest_record)
                elif collection_name == "csdn":
                    latest_record = parse_csdn(latest_record)
                elif collection_name == "openeye":
                    latest_record = parse_openeye(latest_record)
                elif collection_name == "pmcaff":
                    latest_record = parse_pmcaff(latest_record)
                elif collection_name == "tencent_news":
                    latest_record = parse_tencent_news(latest_record)
                elif collection_name == "woshipm":
                    latest_record = parse_woshipm(latest_record)
                elif collection_name == "xueqiu":
                    latest_record = parse_xueqiu(latest_record)
                elif collection_name == "yiche":
                    latest_record = parse_yiche(latest_record)
                elif collection_name == "youshedubao":
                    latest_record = parse_youshedubao(latest_record)
                elif collection_name == "youxiputao":
                    latest_record = parse_youxiputao(latest_record)
                elif collection_name == "zhanku":
                    latest_record = parse_zhanku(latest_record)
                elif collection_name == "zongheng":
                    latest_record = parse_zongheng(latest_record)
                elif collection_name == "hupu":
                    latest_record = parse_hupu(latest_record)
                elif collection_name in ["baidu_hot_search", "hacknews", "historytoday", "3dm", "36kr", "52pj", "baijingchuhai", "dianshangbao", "diyicaijing", "dongchedi", "freebuf", "github", "google_search", "huxiu", "ithome", "kanxue", "kuandaishan", "qichezhijia", "qidian", "shuimu", "sina", "sina_sport", "sina_news", "taipingyang", "taptap"]:
                    latest_record = parse_common(latest_record)
                elif collection_name == "wallstreetcn":
                    latest_record = parse_wallstreetcn(latest_record)
                elif collection_name == "coolan":
                    latest_record = parse_coolan(latest_record)
                local_time = time.localtime(insert_time)
                if collection_name != "douban_movie":
                    data.append({
                        "name": item["name"],
                        "data": latest_record,
                        "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    })
                else:
                    koubei, beimei = parse_douban(latest_record)
                    data.append({
                        "name": "豆瓣电影一周口碑榜",
                        "data": koubei,
                        "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    })
                    data.append({
                        "name": "豆瓣电影北美票房榜",
                        "data": beimei,
                        "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    })
            except Exception as e:
                print(f"Error parsing {collection_name}: {e}")
                print(traceback.format_exc())
        try:
            blog_data = await redis_client.get("myblog")
            if blog_data:
                data.append(json.loads(blog_data))
        except Exception as e:
            print(f"Redis get error: {e}")
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