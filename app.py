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
table_dict = [
    {"name": "B站热榜", "tablename": "bilibili_hot"},
    {"name": "抖音热搜", "tablename": "douyin_hot"},
    {"name": "掘金热榜", "tablename": "juejin_hot"},
    {"name": "少数派热榜", "tablename": "shaoshupai_hot"},
    {"name": "贴吧热议", "tablename": "tieba_topic"},
    {"name": "头条热榜", "tablename": "toutiao_hot"},
    {"name": "微博热搜", "tablename": "weibo_hot_search"},
    {"name": "微信阅读排行榜", "tablename": "wx_read_rank"},
    {"name": "知乎热榜", "tablename": "zhihu_hot_list"},

    {"name": "3DM", "tablename": "3dm"},
    {"name": "36氪", "tablename": "36kr"},
    {"name": "52破解热榜", "tablename": "52pj"},
    {"name": "AcFun热榜", "tablename": "acfun"},
    {"name": "安全客安全快讯", "tablename": "anquanke"},
    {"name": "百度热搜", "tablename": "baidu_hot_search"},
    {"name": "白鲸出海", "tablename": "baijingchuhai"},
    {"name": "CSDN热榜", "tablename": "csdn"},
    {"name": "电商报最新消息", "tablename": "dianshangbao"},
    {"name": "第一财经热榜", "tablename": "diyicaijing"},
    {"name": "懂车帝热搜榜", "tablename": "dongchedi"},
    {"name": "豆瓣电影排行", "tablename": "douban_movie"},
    {"name": "FreeBuf咨询", "tablename": "freebuf"},
    {"name": "GitHub Trending", "tablename": "github"},
    {"name": "Google 热搜", "tablename": "google_search"},
    {"name": "虎扑社区热帖", "tablename": "hupu"},
    {"name": "虎嗅热文", "tablename": "huxiu"},
    {"name": "IT之家热榜", "tablename": "ithome"},
    {"name": "开眼", "tablename": "openeye"},
    {"name": "看雪热门", "tablename": "kanxue"},
    {"name": "宽带山热榜", "tablename": "kuandaishan"},
    {"name": "PMCAFF精选", "tablename": "pmcaff"},
    {"name": "汽车之家热帖榜", "tablename": "qichezhijia"},
    {"name": "起点榜单", "tablename": "qidian"},
    {"name": "水木社区热门话题", "tablename": "shuimu"},
    {"name": "新浪热门", "tablename": "sina"},
    {"name": "新浪体育热门", "tablename": "sina_sport"},
    {"name": "新浪新闻热门", "tablename": "sina_news"},
    {"name": "太平洋汽车热门", "tablename": "taipingyang"},
    {"name": "TapTap热门", "tablename": "taptap"},
    {"name": "腾讯新闻热点榜", "tablename": "tencent_news"},
    {"name": "人人都是产品经理热门", "tablename": "woshipm"},
    {"name": "雪球热门", "tablename": "xueqiu"},
    {"name": "易车热门", "tablename": "yiche"},
    {"name": "优设读报", "tablename": "youshedubao"},
    {"name": "游戏葡萄文章推荐", "tablename": "youxiputao"},
    {"name": "站酷榜单", "tablename": "zhanku"},
    {"name": "纵横24小时畅销榜", "tablename": "zongheng"}
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
                elif collection_name in ["baidu_hot_search", "3dm", "36kr", "52pj", "baijingchuhai", "dianshangbao", "diyicaijing", "dongchedi", "freebuf", "github", "google_search", "hupu", "huxiu", "ithome", "kanxue", "kuandaishan", "qichezhijia", "qidian", "shuimu", "sina", "sina_sport", "sina_news", "taipingyang", "taptap"]:
                    latest_record = parse_common(latest_record)
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