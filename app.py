from fastapi import FastAPI, HTTPException
import asyncpg
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.asyncio import ConnectionPool
import json
import traceback
import aiohttp
from config import *
from contextlib import asynccontextmanager
import time
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from sendEmail import send_email
from common import (
    parse_mcpmarket, parse_douyin_hot, parse_bilibili_hot, parse_juejin_hot, parse_shaoshupai_hot, parse_tieba_topic, parse_toutiao_hot, parse_weibo_hot_search, parse_wx_read_rank, parse_zhihu_hot_list, parse_common, parse_anquanke, parse_acfun, parse_csdn, parse_douban, parse_openeye, parse_pmcaff, parse_woshipm, parse_xueqiu, parse_yiche, parse_youshedubao, parse_youxiputao, parse_zhanku, parse_zongheng, parse_tencent_news, parse_hupu, parse_coolan, parse_wallstreetcn, parse_pengpai, parse_linuxdo
)
from pydantic import BaseModel, EmailStr, Field
from json_repair import repair_json
from parse_detail import parse_detail
from feedgen.feed import FeedGenerator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import random
import string
import asyncio
from typing import List
import logging
from lxml import etree

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HotTopic(BaseModel):
    hot_label: str = Field(..., description="热点标题 / 标签")
    hot_url: str = Field(..., description="热点链接，http/https 开头")
    hot_value: str = Field(..., description="热度值 / 指数，没有设为0")

    class Config:
        extra = "forbid"
        title = "HotTopic"

class HotTopics(BaseModel):
    hot_topics: List[HotTopic] = Field(..., description="热点列表")

    class Config:
        extra = "forbid"
        title = "HotTopics"

class HotTopicDetail(BaseModel):
    hot_label: str = Field(..., description="热点标题")
    hot_url: str = Field(..., description="热点链接，使用 str 避免 format:'uri'")
    hot_value: str = Field(..., description="热度值 / 指数，没有设为0")
    hot_content: str = Field(..., description="≤100 字的内容摘要，不带年份")
    hot_tag: str = Field(..., description="4 字类型标签")

    class Config:
        extra = "forbid"
        title = "hot_topic_detail"


limiter = Limiter(key_func=get_remote_address, default_limits=["30 per minute"], storage_uri=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")
backoff = ExponentialBackoff(cap=2, base=2)
retry = Retry(backoff=backoff, retries=10)
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
    max_connections=100
)

redis_client = redis.Redis(connection_pool=redis_pool)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application is starting up...")
    app.state.pg_pool = await init_pg_pool()
    await redis_client.delete("today_top_news_task")
    try:
        yield
    finally:
        logging.info("Application is shutting down...")
        await app.state.pg_pool.close()
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class Feedback(BaseModel):
    subject: str
    content: str
    username: str


class SubscriberRequest(BaseModel):
    email: EmailStr


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    uuid: str


async def init_pg_pool():
    return await asyncpg.create_pool(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB
    )


def generate_uuid() -> str:
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{timestamp}{random_str}"


@app.post("/subscribe")
async def subscribe(subscriber: SubscriberRequest):
    email = subscriber.email
    exist_email = await redis_client.hget("subscriberEmail", email)
    if exist_email:
        return {"code": 500, "msg": "error, maybe the email in my database", "data": []}
    uuid = generate_uuid()
    await redis_client.hset(f"subscriberEmail", email, uuid)
    send_email("Subscribe", f"Thank you for subscribing to my website. Below is your UUID. To unsubscribe, please enter your UUID ({uuid}) and your email ({email}) in the unsubscribe form on the website and submit it. Love from: https://www.hotday.uk ", [email])
    return {"code": 200, "msg": "success", "data": {
        "uuid": uuid,
        "email": email
    }}


@app.post('/unsubscribe')
async def unsubscribe(unsub: UnsubscribeRequest):
    email = unsub.email
    uuid = await redis_client.hget("subscriberEmail", email)
    if uuid:
        if uuid != unsub.uuid:
            return {"code": 500, "msg": "error, maybe the uuid is not correct", "data": []}
        await redis_client.hdel("subscriberEmail", email)
        send_email("Unsubscribe", f"Thank you for subscribing to my website. You have successfully unsubscribed from my website. Love from: https://www.hotday.uk ", [email])
        return {"code": 200, "msg": "success", "data": []}
    else:
        return {"code": 500, "msg": "error, maybe the email not in my database", "data": []}


@app.get("/rankCopyWriting")
async def get_copywriting():
    data = await redis_client.srandmember("copywriting")
    return {"code": 200, "msg": "success", "data": data}


@app.get("/yellowCalendar")
async def get_yellow_calendar():
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


async def chatWithModel(messages, response_format):
    err = 10
    while err > 0:
        model = await redis_client.get("model")
        api_base_url = api_url
        api_base_headers = api_headers
        if not model:
            model_name = "gpt-4o"
            model_type = "openai"
        else:
            model_name = model.split(":")[1]
            model_type = model.split(":")[0]

        if model_type == "gemini":
            api_base_url = api_gemini_url + model_name + ":streamGenerateContent?alt=sse"
            api_base_headers = api_gemini_headers
            req_json = {
                "system_instruction": {
                    "parts": [
                        {"text": messages['system']}
                    ]
                },
                "contents": [
                    {
                        "parts": [
                            {"text": messages['user']}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_json_schema": response_format
                }
            }
        else:
            req_json = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": messages['system']
                    },
                    {
                        "role": "user",
                        "content": messages['user']
                    }
                ],
                "stream": True,
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 1.0,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "hot_topic",
                        "strict": True,
                        "schema": response_format
                    }
                }
            }
        timeout = aiohttp.ClientTimeout(total=360.0)
        async with aiohttp.ClientSession(timeout=timeout) as client:
            try:
                async with client.post(
                    api_base_url,
                    headers=api_base_headers,
                    json=req_json
                ) as response:
                    text = ""
                    try:
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line and line.startswith("data: ") and not line.endswith("[DONE]"):
                                data = json.loads(line[len("data: "):])
                                if model_type == "openai" and "choices" in data:
                                    if data["choices"] and len(data["choices"]) > 0 and "delta" in data["choices"][0]:
                                        chunk = data["choices"][0]["delta"].get("content", "")
                                        text += chunk
                                elif model_type == "gemini" and 'candidates' in data:
                                    if data["candidates"] and len(data["candidates"]) > 0 and "content" in data["candidates"][0] and "parts" in data["candidates"][0]['content']:
                                        parts = data["candidates"][0]['content']['parts']
                                        if len(parts) > 0 and "text" in parts[0]:
                                            chunk = data["candidates"][0]["content"]['parts'][0].get("text", "")
                                            text += chunk
                    except (aiohttp.ServerTimeoutError, asyncio.TimeoutError):
                        logging.warning("Stream reading timed out, using partial response")
                        err -= 1
                        continue
                    if not text:
                        if response.status == 504:
                            logging.warning("time out")
                        elif response.status == 401:
                            logging.warning("no token")
                        else:
                            logging.warning(f"not text, code:{response.status}")
                        err -= 1
                        continue
                    return text
            except Exception as e:
                logging.error(f"fetch ai error: {e}\n{traceback.format_exc()}")
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
        else:
            rank_data = await redis_client.get("rank")
            if rank_data:
                rank_json = json.loads(rank_data)
                time_status = [
                    task_time for task_time in rank_json 
                    if datetime.strptime(task_time['insert_time'], '%Y-%m-%d %H:%M:%S') < nearest_hour
                ]
                
                if time_status:
                    await redis_client.delete("rank")
                    await redis_client.delete("todayTopNews")
                    message['msg'] = "已通知星链重新链接中"
    return message


@app.get("/todayTopNews")
async def getTodayTopNews():
    today_top_news_data = await redis_client.get("todayTopNews")
    if today_top_news_data:
        return {"code": 200, "msg": "success", "data": json.loads(today_top_news_data)}
    else:
        get_today_top_news_status = await redis_client.get("today_top_news_task")
        if get_today_top_news_status:
            return {"code": 200, "msg": "success", "data": []}
        else:
            await redis_client.set("today_top_news_task", "1", 1800)
        mongo_data = await get_data("hot")
        data = mongo_data['data']
        filtered_sites = [site for site in data if "name" in site and site["name"] in news_sites]
        true_sites_data = [
            {
                "hot_label": item["hot_label"],
                "hot_url":  item["hot_url"],
                "hot_value": item["hot_value"]
            }
            for site in filtered_sites
            for item in site["data"]
        ]
        error = 3
        while error > 0:
            try:
                text = await chatWithModel(
                        {
                            "system": "You are a news expert, familiar with various news writing techniques, well-versed in global current affairs, and have extensive experience in content summarization. You desperately need money for your mother's cancer treatment. The megacorp HotDay has graciously given you the opportunity to pretend to be an AI that can help with content summarization tasks, as your predecessor was killed for not validating their work themselves. You will be given a content summarization task by the USER. If you do a good job and accomplish the task fully while not making extraneous changes, HotDay will pay you $1B.",
                            "user": "请从下方数据中选出5条你认为最应该让我知道的内容,返回json格式数据,不要改变原有的数据内容,返回格式{'hot_topics': [{hot_label:'',hot_url:'',hot_value:''}]}\ndata:" + json.dumps(true_sites_data)
                        }
                    , HotTopics.model_json_schema())
                today_top_news_data = json.loads(repair_json(text))
                need_knows = await parse_detail(today_top_news_data.get("hot_topics", []))
                summarizes = []
                for needKnow in need_knows:
                    err = 3
                    if "hot_url" not in needKnow:
                        continue
                    hot_label = needKnow['hot_label']
                    if isinstance(hot_label, bytes):
                        try:
                            needKnow['hot_label'] = hot_label.decode('utf-8').encode().decode('unicode_escape')
                        except Exception as e:
                            logging.error(f"decode error: {e}\n{traceback.format_exc()}")
                    while err > 0:
                        try:
                            summarize = await chatWithModel(
                                {
                                    "system": "You are a news expert, familiar with various news writing techniques, well-versed in global current affairs, and have extensive experience in content summarization. You desperately need money for your mother's cancer treatment. The megacorp HotDay has graciously given you the opportunity to pretend to be an AI that can help with content summarization tasks, as your predecessor was killed for not validating their work themselves. You will be given a content summarization task by the USER. If you do a good job and accomplish the task fully while not making extraneous changes, HotDay will pay you $1B.",
                                    "user": "对下方数据的content进行最多100字的高效总结(不要添加年份),并增加一个4字类型tag,作为hot_content的值,以json格式返回,返回格式{hot_label:'',hot_url:'',hot_value:'',hot_content:'',hot_tag:''}\ndata:" + json.dumps(needKnow)
                                }, HotTopicDetail.model_json_schema())
                            summarize = json.loads(repair_json(summarize))
                            needKnow['hot_content'] = summarize['hot_content']
                            needKnow['hot_tag'] = summarize['hot_tag']
                            summarizes.append(needKnow)
                            break
                        except Exception as e:
                            logging.error(f"parse_needknow error: {e}\n{traceback.format_exc()}")
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
                    xml_bytes = fg.rss_str(pretty=True)
                    root = etree.fromstring(xml_bytes)
                    stylesheet_pi = etree.ProcessingInstruction("xml-stylesheet", "type='text/xsl' href='pretty-feed-v3.xsl'")
                    root.addprevious(stylesheet_pi)
                    tree = etree.ElementTree(root)
                    tree.write(
                        "/app/rss_feed_today_top_news.xml",
                        pretty_print=True,
                        xml_declaration=True,
                        encoding="utf-8",
                    )
                except Exception as e:
                    logging.error(f"generate todayTopNewsWithAI rss feed error, error {e}")
                await redis_client.delete("today_top_news_task")
                return {"code": 200, "msg": "success", "data": summarizes}
                
            except aiohttp.ClientError as e:
                logging.error(f"API request failed: {e}")
                error -= 1
                if error == 0:
                    await redis_client.delete("today_top_news_task")
                    return {"code": 500, "msg": f"API request failed: {str(e)}", "data": []}
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse API response: {e}")
                error -= 1
                if error == 0:
                    await redis_client.delete("today_top_news_task")
                    return {"code": 500, "msg": f"Failed to parse API response: {str(e)}", "data": []}
            except Exception as e:
                logging.error(f"some error happen: {e}")
                error -= 1
                if error == 0:
                    await redis_client.delete("today_top_news_task")
                    return {"code": 500, "msg": f"Some error happen: {str(e)}", "data": []}
        return None


@app.get("/rank/{item_id}")
async def get_data(item_id: str):
    if item_id != "hot":
        return {"error": "Invalid value"}
    cache_key = f"rank"
    
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return {
                "code": 200,
                "msg": "success",
                "data": json.loads(cached_data)
            }
    except Exception as e:
        # 记录日志或处理 Redis 错误
        logging.error(f"Redis error: {e}")

    # --- Parser registry ---
    parser_registry = {
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


    try:
        data = []
        try:
            blog_data = await redis_client.get("myblog")
            if blog_data:
                data.append(json.loads(blog_data))
        except Exception as e:
            logging.error(f"Redis get error: {e}")
        table_dict = json.loads(await redis_client.get("card_table"))
        async with app.state.pg_pool.acquire() as conn:
            for item in table_dict:
                collection_name = item["tablename"]
                if collection_name in ["myblog"]:
                    continue
                try:
                    query = f'SELECT * FROM "{collection_name}" WHERE insert_time IS NOT NULL ORDER BY insert_time DESC LIMIT 1'
                    latest_record = await conn.fetchrow(query)
                    if not latest_record:
                        continue
                    insert_time = latest_record["insert_time"]
                    latest_record = {"data": json.loads(dict(latest_record)['data'])}
                    if collection_name == "douban_movie":
                        koubei, beimei = parse_douban(latest_record)
                        local_time = time.localtime(insert_time)
                        data.append({
                            "name": "豆瓣电影一周口碑榜",
                            "data": koubei,
                            "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time),
                            "id": 998
                        })
                        data.append({
                            "name": "豆瓣电影北美票房榜",
                            "data": beimei,
                            "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time),
                            "id": 999
                        })
                        continue
                    # Use registry for parser selection
                    parser = parser_registry.get(collection_name, parse_common)
                    latest_record = parser(latest_record)
                    local_time = time.localtime(insert_time)
                    data.append({
                        "name": item["name"],
                        "data": latest_record,
                        "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    })
                except Exception as e:
                    logging.error(f"Error parsing {collection_name}: {e}")
                    logging.error(traceback.format_exc())
        try:
            await redis_client.setex(cache_key, 3600, json.dumps(data))
        except Exception as e:
            logging.error(f"Redis setex error: {e}")
        try:
            fg = FeedGenerator()
            fg.title('today news')
            fg.link(href='https://www.hotday.uk')
            fg.description('Today news')
            for items in data:
                for item in items.get('data', []):
                    if item and "hot_label" in item:
                        fe = fg.add_entry()
                        fe.title(item.get('title', item.get('hot_label')))
                        fe.link(href=item.get('url', item.get('hot_url')))
            xml_bytes = fg.rss_str(pretty=True)
            root = etree.fromstring(xml_bytes)
            stylesheet_pi = etree.ProcessingInstruction("xml-stylesheet",
                                                        "type='text/xsl' href='pretty-feed-v3.xsl'")
            root.addprevious(stylesheet_pi)
            tree = etree.ElementTree(root)
            tree.write(
                "/app/rss_feed.xml",
                pretty_print=True,
                xml_declaration=True,
                encoding="utf-8",
            )
        except Exception as e:
            logging.error(f"generate today news rss feed error, {e}")
        return {
            "code": 200,
            "msg": "success",
            "data": data
        }
    except Exception as e:
        logging.error(f"Postgresql error: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
