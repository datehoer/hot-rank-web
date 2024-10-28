import json
from curl_cffi import requests
from pyquery import PyQuery as pq
import redis
from config import *
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)
html_content = requests.get("https://www.huangli.com/").text

doc = pq(html_content)

# 提取年、月、日的干支、生肖和纳音信息
horoscope_data = []
for horoscope in doc(".lunars-b .l .horoscope").items():
    hit = horoscope.find(".hit").text()
    gz = horoscope.find(".gz").text()
    zodiac = horoscope.find(".zodiac").text()
    nayin = horoscope.find(".nayin").text()
    horoscope_data.append({
        "hit": hit,
        "gz": gz,
        "zodiac": zodiac,
        "nayin": nayin
    })

# 分别提取“宜”和“忌”事项
yi_list = [a.text() for a in doc(".lunars-b .l .yi-ji a").items()]
ji_list = [a.text() for a in doc(".lunars-b .r .yi-ji a").items()]

# 提取吉神宜趋
jishen = doc(".lunars-b .l .shen-sha p").text().split(",")

# 提取凶煞宜忌
xiongsha = doc(".lunars-b .r .shen-sha p").text().split(",")

# 提取彭祖百忌和相冲
pengzu_baiji = doc(".lunars-b .l .pz-chong .title:contains('彭祖百忌') + .text").text()
xiang_chong = doc(".lunars-b .l .pz-chong .title:contains('相冲') + .text").text()

# 提取月名、物候、月相
yue_data = []
for item in doc(".lunars-b .l .yz-wh-yx div").items():
    title = item.find(".title").text()
    text = item.find(".text").text()
    yue_data.append({"title": title, "text": text})

# 组织成最终的字典
result = {
    "horoscope_data": horoscope_data,
    "yi_list": yi_list,
    "ji_list": ji_list,
    "jishen": jishen,
    "xiongsha": xiongsha,
    "pengzu_baiji": pengzu_baiji,
    "xiang_chong": xiang_chong,
    "yue_data": yue_data
}
json_result = json.dumps(result, ensure_ascii=False, indent=4)
redis_client.set("yellowCalendar", json_result)