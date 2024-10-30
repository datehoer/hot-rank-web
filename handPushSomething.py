import redis
from config import *
import json
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

online_movies = [{
    "name": "播剧影视网",
    "url": "https://www.boju.cc/"
},{
    "name": "Lemo",
    "url": "https://lemo.us.kg/"
},{"name": "555电影", "url": "https://www.55flix.com/"},
    {"name": "低端影视", "url": "https://ddys.pro/"},
    {"name": "LIBVIO", "url": "https://www.libvio.pro/"},
    {"name": "热播之家", "url": "https://rebozj.pro/"},
    {"name": "蛋蛋赞影院", "url": "https://www.dandanzan.club/"},
    {"name": "大师兄影视", "url": "https://dsxys.pro/"},
    {"name": "楓林網", "url": "https://imaple8.co/"},
    {"name": "Gimy 劇迷", "url": "https://gimy.im/"},
    {"name": "Gimy小鴨影音", "url": "https://gimy.cc/"},
    {"name": "94i影城", "url": "https://94itv.app/"},
    {"name": "Vidhub视频库", "url": "https://vidhub.tv/"},
    {"name": "厂长资源", "url": "https://www.czzy77.com/"},
    {"name": "HDmoli", "url": "https://www.hdmoli.pro/"},
    {"name": "电影先生", "url": "https://dyxs39.com/"},
    {"name": "4k影视", "url": "https://www.4kvm.net/"},
    {"name": "美柏影视", "url": "https://www.mp4br.com/"},
    {"name": "素白白影视", "url": "https://www.subaibaiys.com/"},
    {"name": "OK电影院", "url": "https://www.okdyy.com/"},
    {"name": "奈飞中文影视", "url": "https://netfly.fun/"},
    {"name": "毒舌电影", "url": "https://www.duse1.com/"},
    {"name": "胖虎免费svip影视", "url": "https://www.phyt.net/"},
    {"name": "五五短剧", "url": "https://www.duanju55.com/"},
    {"name": "短剧网", "url": "https://www.duanju001.com/"},
    {"name": "短剧搜索", "url": "https://www.kdocs.cn/l/cp1MFwlimAAm?R=L1MvMQ=="},
    {"name": "红果短剧", "url": "https://novelquickapp.com/hongguo"},
    {"name": "全民短剧", "url": "https://playlet.kuwo.cn/"},
    {"name": "短剧狗", "url": "https://duanjugou.top/"}
]

for movie in online_movies:
    redis_client.sadd("online_movies", json.dumps(movie))
