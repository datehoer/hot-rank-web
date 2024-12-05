import json
import time
import redis
from urllib.parse import urljoin
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from curl_cffi import requests
from pyquery import PyQuery as pq

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

    # 保存到 Redis
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
