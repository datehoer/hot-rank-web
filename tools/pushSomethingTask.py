import json
import time
import redis
from urllib.parse import urljoin
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, api_headers, api_url
from curl_cffi import requests
from pyquery import PyQuery as pq
import json_repair


# 初始化 Redis 客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def scrape_huangli():
    url = "https://www.laohuangli.net/"
    html_content = requests.get(url).text
    doc = pq(html_content)
    data = {}

    # 左侧年份、生肖、五行信息
    left_divs = doc("td[class='tr-p0'] div")
    data['year_info'] = [
        {
            "label": pq(span.eq(0)).text(),
            "zodiac": pq(span.eq(1)).text(),
            "element": pq(span.eq(2)).text()
        }
        for div in left_divs
        for span in [pq(div).find("span")]
    ]

    # 提取公历和农历信息
    calendar_info = doc("td[class='bg-table'] .middle-rowspan")
    data['gregorian_calendar'] = calendar_info.find("p").eq(0).text()
    data['lunar_calendar'] = calendar_info.find("p").eq(1).text()

    # 提取宜和忌信息
    good_div = doc(".table-three-div").eq(0)
    bad_div = doc(".table-three-div").eq(1)
    data['good_actions'] = [
        pq(span).text() for span in good_div.find("span") if pq(span).text()
    ]
    data['bad_actions'] = [
        pq(span).text() for span in bad_div.find("span") if pq(span).text()
    ]

    # 提取彭祖百忌和相冲
    fourth_row = doc(".table-four-tr")
    data['pengzu_bai_ji'] = fourth_row.find(".col-td2").eq(0).find(".icon-none").text()
    data['xiang_chong'] = fourth_row.find(".col-td2").eq(1).find(".icon-none").text()

    # 提取胎神信息
    data['tai_shen'] = [
        pq(span).text()
        for span in fourth_row.find(".col-td2").eq(2).find(".icon-none")
    ]

    # 提取吉神和凶煞
    fifth_row = doc(".table-five-div")
    data['ji_shen'] = fifth_row.eq(0).find("p").text().replace(",", "").split()
    data['xiong_sha'] = fifth_row.eq(2).find("p").text().replace(",", "").split()

    # 提取表格中的月份、物候等信息
    month_table = doc("table")
    data['month_table'] = [
        {
            pq(td.eq(0)).text(): pq(td.eq(1)).text()
            for td in pq(tr).find("td").items()
        }
        for tr in month_table.find("tr").items()
    ]
    if data['lunar_calendar'] == "":
        chat_get_calendar()
    else:
        json_result = json.dumps(data, ensure_ascii=False, indent=4)
        redis_client.set("yellowCalendar", json_result)


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
                  "role": "system",
                  "content": "你是一个黄历助手，熟悉黄历计算，现在阳历日期是"+time.strftime("%Y-%m-%d", time.localtime())
                },
                {
                    "role": "user",
                    "content": "给我今天的黄历信息,lunar_calendar需要是天干地支纪年法 农历月日 生肖，需要包含以以下格式返回给我，返回一个json格式的数据："+json.dumps({"gregorian_calendar": "", "lunar_calendar": "", "good_actions": [], "bad_actions": []})
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
        redis_client.set("yellowCalendar", json_result)


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
