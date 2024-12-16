from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.asyncio import ConnectionPool
import json
import traceback
import httpx
from config import *
import time
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from sendEmail import send_email
from common import *
from pydantic import BaseModel
from json_repair import repair_json
from parse_detail import parse_detail
from feedgen.feed import FeedGenerator
import traceback
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
async def chatWithModel(messages, check_list=True):
    err = 10
    while err > 0:
        model = await redis_client.get("model")
        async with httpx.AsyncClient(timeout=httpx.Timeout(360.0)) as client:
            try:
                response = await client.post(
                    api_url,
                    headers=api_headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0,
                        "response_format": {"type": "json_object"}
                    }
                )
                text = ""
                try:
                    async for line in response.aiter_lines():
                        if line and line.startswith("data: ") and not line.endswith("[DONE]"):
                            data = json.loads(line[len("data: "):])
                            if "choices" in data:
                                if data["choices"] and len(data["choices"]) > 0 and "delta" in data["choices"][0]:
                                    chunk = data["choices"][0]["delta"].get("content", "")
                                    text += chunk
                except httpx.ReadTimeout:
                    print("Stream reading timed out, using partial response")
                    err -= 1
                    continue
                if not text:
                    if response.status_code == 504:
                        print("time out")
                    elif response.status_code == 401:
                        print("no token")
                    else:
                        print("not text, code:"+str(response.status_code))
                    err -= 1
                    continue
                if check_list and "hot_value" not in text:
                    print('no hot value')
                    err -= 1
                    continue
                if not check_list and "hot_tag" not in text:
                    print('no hot tag')
                    err -= 1
                    continue
                return text
            except Exception as e:
                print("fetch ai error: " + str(e) + traceback.format_exc())
                err -= 1
    return ""
@app.get("/holiday")
async def getHoliday():
    holidays = await redis_client.get("holidays")
    return {"code": 200, "msg": "success", "data": json.loads(holidays)}
@app.get("/refresh")
async def refresh():
    ttl_time_second = await redis_client.ttl("rank")
    message = {
            "code": 200,
            "msg": "星链回复是最新数据啦",
            "data": []
        }
    if ttl_time_second:
        current_time = datetime.now()
        total_ttl = timedelta(hours=1)
        creation_time = current_time - (total_ttl - timedelta(seconds=ttl_time_second))
        nearest_hour = current_time.replace(minute=0, second=0, microsecond=0)
        if creation_time < nearest_hour:
            await redis_client.delete("rank")
            await redis_client.delete("todayTopNews")
            message['msg'] = "已通知星链重新链接中"
    return message

@app.get("/todayTopNews")
async def getTodayTopNews():
    todayTopNewsData = await redis_client.get("todayTopNews")
    if todayTopNewsData:
        return {"code": 200, "msg": "success", "data": json.loads(todayTopNewsData)}
    else:
        mongoData = await get_data("hot")
        data = mongoData['data']
        filtered_sites = [site for site in data if site["name"] in news_sites]
        error = 3
        while error > 0:
            try:
                text = await chatWithModel([
                        {
                            "role": "system",
                            "content": "你是一个新闻专家,熟悉各种新闻编写手段,并且熟知全球时事"
                        },
                        {
                            "role": "user",
                            "content": "请从下方数据中选出10条你认为最应该让我知道的内容,返回json格式数据,返回格式{'hot_topics': [{hot_label:'',hot_url:'',hot_value:''}]}\ndata:" + json.dumps(filtered_sites)
                        }
                    ])
                todayTopNewsData = json.loads(repair_json(text))
                if "messages" in todayTopNewsData:
                    messages = todayTopNewsData["messages"]
                    if messages and len(messages) == 1:
                        todayTopNewsData = messages[0]
                        if "content" in todayTopNewsData:
                            todayTopNewsData = todayTopNewsData['content']
                if "hot_topics" in todayTopNewsData:
                    todayTopNewsData = todayTopNewsData['hot_topics']
                if not isinstance(todayTopNewsData, list):
                    error -=  1
                    continue
                needKnows = await parse_detail(todayTopNewsData)
                summarizes = []
                for needKnow in needKnows:
                    err = 3
                    while err > 0:
                        try:
                            summarize = await chatWithModel([
                                {
                                    "role": "system",
                                    "content": "你是一个新闻专家,熟悉各种新闻编写手段,并且熟知全球时事,并且有丰富的内容总结经验"
                                },
                                {
                                    "role": "user",
                                    "content": "对下方数据的content进行最多300字的高效总结(不要添加年份),并增加一个4字类型tag,作为hot_content的值,以json格式返回,返回格式{hot_label:'',hot_url:'',hot_value:'',hot_content:'',hot_tag:''}\ndata:" + json.dumps(needKnow)
                                }
                            ], False)
                            summarize = json.loads(repair_json(summarize))
                            if "messages" in summarize:
                                summarize = summarize["messages"]
                                if summarize and len(summarize) == 1:
                                    summarize = summarize[0]
                                    if "content" in summarize:
                                        summarize = summarize['content']
                            if "content" in needKnow:
                                del needKnow['content']
                            if "hot_label" not in summarize:
                                continue
                            needKnow['hot_content'] = summarize['hot_content']
                            needKnow['hot_tag'] = summarize['hot_tag']
                            summarizes.append(needKnow)
                            break
                        except Exception as e:
                            print("parse_needknow error:" + str(e) + traceback.format_exc())
                            err -= 1
                await redis_client.setex("todayTopNews", 3600, json.dumps(summarizes))
                try:
                    fg = FeedGenerator()
                    fg.title('todayTopNewsWithAI')
                    fg.link(href='https://www.hotday.uk')
                    fg.description('Today top news with AI')
                    for item in summarizes:
                        fe = fg.add_entry()
                        fe.title(item.get('title', item['hot_label']))
                        fe.link(href=item.get('url', item['hot_url']))
                        fe.description(item.get('description', item['hot_content']))
                    fg.rss_file('/app/rss_feed_today_top_news.xml')
                except Exception as e:
                    print("generate todayTopNewsWithAI rss feed error")
                return {"code": 200, "msg": "success", "data": summarizes}
                
            except httpx.RequestError as e:
                print(f"API request failed: {str(e)}")
                error -= 1
                if error == 0:
                    return {"code": 500, "msg": f"API request failed: {str(e)}", "data": []}
            except json.JSONDecodeError as e:
                print(f"Failed to parse API response: {str(e)}")
                error -= 1
                if error == 0:
                    return {"code": 500, "msg": f"Failed to parse API response: {str(e)}", "data": []}
            except Exception as e:
                print(f"some error happen: {str(e)}")
                error -= 1
                if error == 0:
                    return {"code": 500, "msg": f"Some error happen: {str(e)}", "data": []}
            
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
                elif collection_name == "wallstreetcn":
                    latest_record = parse_wallstreetcn(latest_record)
                elif collection_name == "coolan":
                    latest_record = parse_coolan(latest_record)
                elif collection_name == "pengpai":
                    latest_record = parse_pengpai(latest_record)
                elif collection_name not in ['douban_movie']:
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
        try:
            fg = FeedGenerator()
            fg.title('today news')
            fg.link(href='https://www.hotday.uk')
            fg.description('Today news')
            for items in data:
                for item in items['data']:
                    if item and "hot_label" in item:
                        fe = fg.add_entry()
                        fe.title(item.get('title', item['hot_label']))
                        fe.link(href=item.get('url', item['hot_url']))
            fg.rss_file('/app/rss_feed.xml')
        except Exception as e:
            print("generate today news rss feed error")
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