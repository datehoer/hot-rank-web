import json
import time
import redis
from urllib.parse import urljoin
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, api_headers, api_url
from curl_cffi import requests
from pyquery import PyQuery as pq
import json_repair
from datetime import datetime, timedelta


# 初始化 Redis 客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def scrape_huangli():
    url = "https://www.huangli123.net/"
    try:
        html_content = requests.get(url).text
        doc = pq(html_content)
        # 解析公历日期
        gregorian_calendar = doc('.huang_center h2').text().strip()

        # 解析农历日期
        lunar_calendar = doc('.huang_center h3').text().strip()

        # 解析宜事项
        good_actions = []
        good_spans = doc('.huangli_yiji:first p span')
        for span in good_spans.items():
            action = span.text().strip()
            if action and action != "****":  # 过滤掉占位符
                good_actions.append(action)

        # 解析忌事项
        bad_actions = []
        bad_spans = doc('.huangli_yiji:last p span')
        for span in bad_spans.items():
            action = span.text().strip()
            if action:
                bad_actions.append(action)

        result = {
            "gregorian_calendar": gregorian_calendar,
            "lunar_calendar": lunar_calendar,
            "good_actions": good_actions,
            "bad_actions": bad_actions
        }
        json_result = json.dumps(result, ensure_ascii=False, indent=4)
        redis_client.set("yellowCalendar", json_result)
    except:
        chat_get_calendar()

def chat_get_calendar():
    data = redis_client.get("yellowCalendar")
    need_chat = False
    if data:
        data = json.loads(data)
        if "lunar_calendar" in data:
            if data['lunar_calendar'] == "":
                need_chat = True
        else:
            need_chat = True
    else:
        need_chat = True
    if need_chat:
        today = time.strftime("%Y-%m-%d", time.localtime())
        res = requests.post(api_url, headers=api_headers, json={
            "messages": [
                {
                    "role": "user",
                    "content": "你是一个黄历助手，熟悉黄历计算，今天阳历日期是"+today + "给我今天的黄历信息,lunar_calendar需要是天干地支纪年法 农历月日 生肖，需要包含以以下格式返回给我，返回一个json格式的数据："+json.dumps({"gregorian_calendar": "", "lunar_calendar": "", "good_actions": [], "bad_actions": []})
                }
            ],
            "model": "deepseek-chat",
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
            "stream": True
        }, stream=True)
        text = ""
        for line in res.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line and line.startswith("data: ") and not line.endswith("[DONE]"):
                    data = json.loads(line[len("data: "):])
                    if "choices" in data:
                        if data["choices"] and len(data["choices"]) > 0 and "delta" in data["choices"][0]:
                            chunk = data["choices"][0]["delta"].get("content", "")
                            text += chunk
        data = json.loads(json_repair.repair_json(text))
        json_result = json.dumps(data, ensure_ascii=False, indent=4)
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        tomorrow_midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
        seconds_until_midnight = int((tomorrow_midnight - now).total_seconds())
        redis_client.set("yellowCalendar", json_result, ex=seconds_until_midnight)


def scrape_datehoer():
    url = "https://www.datehoer.com/"
    res = requests.get(url)
    doc = pq(res.content.decode("utf-8"))

    items = doc(".blog-list div.title")
    blog_list = []

    for item in items.items():
        a = item.find("a")
        title = a.text()
        link = urljoin(url, a.attr('href'))
        blog_list.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": 999999
        })

    result = {
        "name": "Datehoer最新发文",
        "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "data": blog_list
    }

    redis_client.set("myblog", json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    scrape_huangli()
    scrape_datehoer()
