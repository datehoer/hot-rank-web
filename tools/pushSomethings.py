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

# urls = [
#     "https://oss.datehoer.com/default-images/avatar/cutefire_1.png",
#     "https://oss.datehoer.com/default-images/avatar/cutefire_2.png",
#     "https://oss.datehoer.com/default-images/avatar/cutefire_3.png",
#     "https://oss.datehoer.com/default-images/avatar/cutefire_4.png",
#     "https://oss.datehoer.com/default-images/avatar/headphones_1.png",
#     "https://oss.datehoer.com/default-images/avatar/headphones_2.png",
#     "https://oss.datehoer.com/default-images/avatar/headphones_3.png",
#     "https://oss.datehoer.com/default-images/avatar/headphones_4.png",
#     "https://oss.datehoer.com/default-images/avatar/spiderman_1.png",
#     "https://oss.datehoer.com/default-images/avatar/spiderman_2.png",
#     "https://oss.datehoer.com/default-images/avatar/spiderman_3.png",
#     "https://oss.datehoer.com/default-images/avatar/spiderman_4.png"
# ]

# for url in urls:
#     redis_client.sadd("avatar", url)

# texts = [
#     "周だ贱伦てゆ",
#     "お讉莣諾戀ぁ",
#     "祗尖ベ煙Ω圈?",
#     "ヤ茈情kě待",
#     "﹎ì.呦児圜",
#     "⑥星飛ㄚц♀",
#     "⿶莳尙寳ル",
#     "メㄝ界末ㄖ.",
#     "┌蕝薱願創",
#     "℡左掱寫愛",
#     "￠伤…①⑨",
#     "⺌點點頭﹎答",
#     "壞壊deヤωǒ",
#     "⿻?愛の终゛",
#     "╰熹ゞㄡ欠﹎",
#     "ジェ愛隨緣ラ",
#     "☆LèLè☆",
#     "5`⒋з.2.ㄧ",
#     "⿴╪｛张侗學",
#     "ャ⿴國際淫蕩",
#     "僾伱Ъㄩ逅誨",
#     "(_少鈎鈏ωǒ ゛",
#     "｛｛冄坙",
#     "〣咹魵點.√",
#     "╭ブ簡單愛",
#     "(_灬兲使ぺ",
#     "㊣er㈧經de愛",
#     "娓ぁ装ω",
#     "尛鷄侽孖",
#     "⑦穜↘菋噵◇",
#     "⿺﹎單裑m^",
#     "|曐⑦叭|▍",
#     "♂莣鋽濄麮♀ :",
#     "_瑏cuò鞋●",
#     "﹌銥賴▼.",
#     "︶ㄣ冰锋⺗︵",
#     "溈鉨ｗǒ變乖",
#     "╀絕蝂oо`倫",
#     "儰你變乖",
#     "獨特ω銥賴",
#     "に訫隨Ｗǒ變",
#     "風蓅乄無惢￠",
#     "の寳唄;莉児",
#     "ゞ莣鋽ど鍋佉",
#     "しov聽花若北\\",
#     "尐囡壞脾氣",
#     "＂國際尛鷄m",
#     "鶏㈧嘵yáo芓",
#     "誮た尐羅卟ま",
#     "咹靜嘚消失",
#     "№帅馨の戀♂",
#     "●勁儛娚駭ぽ",
#     "鎖骨秀姿色",
#     "學^ō^乖→咗",
#     "⒛ō⑦緟鋅愛",
#     "╰☆╮雨㊣神",
#     "硪◎－◎拽oκ",
#     "冰雪獨爱征",
#     "ヤ寶ы.ゞ児o"
# ]
# for text in texts:
#     redis_client.sadd("username", text)


# copywriting = [
#     "领导说要全力以赴,我选择全身以退。",
#     "工作是人生的调味料,我偏爱淡而无味。",
#     "别人在职场奔跑,我在人生沙发躺平。",
#     "我不是消极怠工,是在用沉默抗议996。",
#     "工位上的我,像一尊栩栩如生的蜡像。",
#     "打工人的双手是魔术师,总能变出各种借口。",
#     "我的工作热情,被朝九晚五消磨殆尽。",
#     "摸鱼是一门艺术,需要天赋和勇气。",
#     "工作是场马拉松,我选择做观众。",
#     "KPI像星星,看得见摸不着。",
#     "我不是不努力,只是把能量用在了摸鱼上。",
#     "工资就像初恋,总觉得不够。",
#     "上班如同修行,摸鱼是顿悟。",
#     "工作效率与工资成反比。",
#     "职场如戏,全靠演技。",
#     "会议室是最好的冥想场所。",
#     "老板的期望像气球,总是吹得太大。",
#     "我的工位是孤岛,我是岛主。",
#     "摸鱼不是懒,是对生活的思考。",
#     "工作日志上写满了'明天'。",
# ]
# for text in copywriting:
#     redis_client.sadd("copywriting", text)

table = [
    {"name": "B站热榜", "tablename": "bilibili_hot"},
    {"name": "抖音热搜", "tablename": "douyin_hot"},
    {"name": "澎湃新闻", "tablename": "pengpai"},
    {"name": "掘金热榜", "tablename": "juejin_hot"},
    {"name": "少数派热榜", "tablename": "shaoshupai_hot"},
    {"name": "加密货币", "tablename": "crypto_coin"},
    {"name": "贴吧热议", "tablename": "tieba_topic"},
    {"name": "头条热榜", "tablename": "toutiao_hot"},
    {"name": "纽约时报", "tablename": "nytimes"},
    {"name": "华尔街日报", "tablename": "wsj"},
    {"name": "彭博新闻", "tablename": "bloomberg"},
    {"name": "金融时报", "tablename": "ft"},
    {"name": "微博热搜", "tablename": "weibo_hot_search"},
    {"name": "知乎热榜", "tablename": "zhihu_hot_list"},
    {"name": "虎扑社区热帖", "tablename": "hupu"},
    {"name": "历史上的今天", "tablename": "historytoday"},
    {"name": "华尔街见闻", "tablename": "wallstreetcn"},
    {"name": "要知", "tablename": "needknow"},
    {"name": "v2ex热门", "tablename": "v2ex"},
    {"name": "nodeseek", "tablename": "nodeseek"},
    {"name": "hostloc", "tablename": "hostloc"},
    {"name": "linuxdo", "tablename": "linuxdo"},
    {"name": "微信阅读排行榜", "tablename": "wx_read_rank"},
    {"name": "Yonhap News Agency", "tablename": "yna"},
    {"name": "Asahi Shimbun", "tablename": "asahi"},
    {"name": "Nippon Hōsō Kyōkai", "tablename": "nhk"},
    {"name": "Fox News", "tablename": "foxnews"},
    {"name": "Russia Today", "tablename": "rt"},
    {"name": "Le Monde", "tablename": "lemonde"},
    {"name": "Daily Mail", "tablename": "dailymail"},
    {"name": "Mumsnet", "tablename": "mumsnet"},
    {"name": "News.com.au", "tablename": "newsau"},
    {"name": "5Channel", "tablename": "fivech"},
    {"name": "Дзен", "tablename": "dzenru"},
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
    {"name": "虎嗅热文", "tablename": "huxiu"},
    {"name": "3DM", "tablename": "3dm"},
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
    {"name": "纵横24小时畅销榜", "tablename": "zongheng"},
    # {"name": "酷安热门话题", "tablename": "coolan"},
    {"name": "hacknews", "tablename": "hacknews"},
]
redis_client.set("card_table", json.dumps(table))

# online_movies = [{
#     "name": "播剧影视网",
#     "url": "https://www.boju.cc/"
# },{
#     "name": "Lemo",
#     "url": "https://lemo.us.kg/"
# },{"name": "555电影", "url": "https://www.55flix.com/"},
#     {"name": "低端影视", "url": "https://ddys.pro/"},
#     {"name": "LIBVIO", "url": "https://www.libvio.pro/"},
#     {"name": "热播之家", "url": "https://rebozj.pro/"},
#     {"name": "蛋蛋赞影院", "url": "https://www.dandanzan.club/"},
#     {"name": "大师兄影视", "url": "https://dsxys.pro/"},
#     {"name": "楓林網", "url": "https://imaple8.co/"},
#     {"name": "Gimy 劇迷", "url": "https://gimy.im/"},
#     {"name": "Gimy小鴨影音", "url": "https://gimy.cc/"},
#     {"name": "94i影城", "url": "https://94itv.app/"},
#     {"name": "Vidhub视频库", "url": "https://vidhub.tv/"},
#     {"name": "厂长资源", "url": "https://www.czzy77.com/"},
#     {"name": "HDmoli", "url": "https://www.hdmoli.pro/"},
#     {"name": "电影先生", "url": "https://dyxs39.com/"},
#     {"name": "4k影视", "url": "https://www.4kvm.net/"},
#     {"name": "美柏影视", "url": "https://www.mp4br.com/"},
#     {"name": "素白白影视", "url": "https://www.subaibaiys.com/"},
#     {"name": "OK电影院", "url": "https://www.okdyy.com/"},
#     {"name": "奈飞中文影视", "url": "https://netfly.fun/"},
#     {"name": "毒舌电影", "url": "https://www.duse1.com/"},
#     {"name": "胖虎免费svip影视", "url": "https://www.phyt.net/"},
#     {"name": "五五短剧", "url": "https://www.duanju55.com/"},
#     {"name": "短剧网", "url": "https://www.duanju001.com/"},
#     {"name": "短剧搜索", "url": "https://www.kdocs.cn/l/cp1MFwlimAAm?R=L1MvMQ=="},
#     {"name": "红果短剧", "url": "https://novelquickapp.com/hongguo"},
#     {"name": "全民短剧", "url": "https://playlet.kuwo.cn/"},
#     {"name": "短剧狗", "url": "https://duanjugou.top/"}
# ]

# for movie in online_movies:
#     redis_client.sadd("online_movies", json.dumps(movie))

# music_list =[
#     {
#         'id': 1,
#         'title': 'Take Me To Your Heart',
#         'cover': "https://oss.datehoer.com/music/cover/TakeMeToYourHeart.jpg",
#         'url': "https://oss.datehoer.com/music/mp3/TakeMeToYourHeart.m4a"
#     },
#     {
#         'id': 2,
#         'title': 'I Really Like You',
#         'cover': "https://oss.datehoer.com/music/cover/ireallylikeyou.jpg",
#         'url': "https://oss.datehoer.com/music/mp3/IReallyLikeYou.m4a"
#     },
#     {
#         'id': 3,
#         'title': 'APT.',
#         'cover': "https://oss.datehoer.com/music/cover/APT.jpg",
#         'url': "https://oss.datehoer.com/music/mp3/APT.m4a"
#     },
#     {
#         'id': 4,
#         'title': 'I Really Like You',
#         'cover': "https://oss.datehoer.com/music/cover/FeelLikeANumber.jpg",
#         'url': "https://oss.datehoer.com/music/mp3/FeelLikeANumber.mp3"
#     }
# ]
# redis_client.set("music", json.dumps(music_list))

# model = "grok-beta"

# redis_client.set("model", model)

# holides = [
#   {
#     "holiday_name": "元旦",
#     "date": "2025-01-01",
#     "timestamp": 1735689600,
#     "remarks": "周三放假1天，不调休。"
#   },
#   {
#     "holiday_name": "春节",
#     "date": "2025-01-28",
#     "timestamp": 1738012800,
#     "remarks": "农历除夕（周二）起放假调休，共8天。1月26日（周日）、2月8日（周六）上班。"
#   },
#   {
#     "holiday_name": "清明节",
#     "date": "2025-04-04",
#     "timestamp": 1743724800,
#     "remarks": "周五起放假，共3天。"
#   },
#   {
#     "holiday_name": "劳动节",
#     "date": "2025-05-01",
#     "timestamp": 1746124800,
#     "remarks": "周四起放假调休，共5天。4月27日（周日）上班。"
#   },
#   {
#     "holiday_name": "端午节",
#     "date": "2025-05-31",
#     "timestamp": 1748630400,
#     "remarks": "周六起放假，共3天。"
#   },
#   {
#     "holiday_name": "国庆节、中秋节",
#     "date": "2025-10-01",
#     "timestamp": 1759276800,
#     "remarks": "周三起放假调休，共8天。9月28日（周日）、10月11日（周六）上班。"
#   }
# ]
# redis_client.set("holidays", json.dumps(holides))