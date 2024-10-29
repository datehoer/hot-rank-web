import requests
import pyquery
import redis
import time
import json
from config import *
from urllib.parse import urljoin
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)
url = "https://www.datehoer.com/"
res = requests.get(url)
doc = pyquery.PyQuery(res.content.decode("utf-8"))
items = doc(".blog-list div.title")
blog_list = []
for item in items:
    a = item.find("a")
    title = a.text
    url = urljoin(url, a.attrib['href'])
    blog_list.append({"hot_label": title, "hot_url": url, "hot_value": 999999})
result = {
    "name": "Datehoer最新发文",
    "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    "data": blog_list
}
redis_client.set("myblog", json.dumps(result))
