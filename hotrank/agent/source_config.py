import json
import logging

from hotrank.agent.tool_registry import SUPPORTED_SEARCH_PLATFORMS
from hotrank.cache import redis_cache


QUERY_SOURCES_REDIS_KEY = "agent:query:sources"

SOURCE_LABELS = {
    "36kr": "36氪",
    "3dm": "3DM",
    "52pj": "吾爱破解",
    "acfun": "AcFun 热榜",
    "anquanke": "安全客",
    "asahi": "朝日新闻",
    "baidu_hot_search": "百度热搜",
    "baijingchuhai": "白鲸出海",
    "bilibili_hot": "Bilibili 热榜",
    "bloomberg": "彭博新闻",
    "coolan": "酷安",
    "crypto_coin": "加密货币",
    "csdn": "CSDN 热榜",
    "dailymail": "Daily Mail",
    "dianshangbao": "电商报",
    "diyicaijing": "第一财经",
    "dongchedi": "懂车帝",
    "douban_movie": "豆瓣电影",
    "douyin_hot": "抖音热搜",
    "dzenru": "Дзен",
    "fivech": "5Channel",
    "foxnews": "Fox News",
    "ft": "金融时报",
    "github": "GitHub Trending",
    "googlenews": "Google News",
    "hacknews": "Hacker News",
    "historytoday": "历史上的今天",
    "hostloc": "Hostloc",
    "hupu": "虎扑",
    "huxiu": "虎嗅",
    "ifanr": "爱范儿",
    "ithome": "IT 之家",
    "jin10": "金十数据",
    "juejin_hot": "掘金热榜",
    "kanxue": "看雪",
    "kuandaishan": "宽带山",
    "lemonde": "Le Monde",
    "linuxdo": "Linux.do",
    "mcpmarket": "MCP Market",
    "mumsnet": "Mumsnet",
    "needknow": "要知",
    "newsau": "News.com.au",
    "nhk": "NHK",
    "nodeseek": "NodeSeek",
    "nytimes": "纽约时报",
    "openeye": "开眼",
    "pengpai": "澎湃新闻",
    "qichezhijia": "汽车之家",
    "qidian": "起点中文网",
    "readhub": "Readhub",
    "rt": "Russia Today",
    "secrss": "安全 RSS",
    "shaoshupai_hot": "少数派",
    "shuimu": "水木社区",
    "sina": "新浪热门",
    "sina_news": "新浪新闻",
    "steam": "Steam",
    "taipingyang": "太平洋汽车",
    "taptap": "TapTap",
    "tencent_news": "腾讯新闻",
    "thehackernews": "The Hacker News",
    "tieba_topic": "贴吧热议",
    "toutiao_hot": "头条热榜",
    "v2ex": "V2EX",
    "wallstreetcn": "华尔街见闻",
    "weibo_hot_search": "微博热搜",
    "woshipm": "人人都是产品经理",
    "wx_read_rank": "微信读书排行榜",
    "xueqiu": "雪球",
    "yiche": "易车",
    "yna": "韩联社",
    "youshedubao": "优设读报",
    "youxiputao": "游戏葡萄",
    "zhanku": "站酷",
    "zongheng": "纵横中文网",
}


def parse_allowed_query_sources(raw_value: str | None) -> list[str]:
    """Return configured sources in the stable supported-source order."""
    if raw_value is None:
        return list(SUPPORTED_SEARCH_PLATFORMS)

    try:
        configured = json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        logging.error(
            "Invalid JSON in Redis key %s",
            QUERY_SOURCES_REDIS_KEY,
        )
        return []

    if not isinstance(configured, list) or not all(
        isinstance(source, str) for source in configured
    ):
        logging.error(
            "Redis key %s must contain a JSON string array",
            QUERY_SOURCES_REDIS_KEY,
        )
        return []

    configured_set = set(configured)
    unsupported = configured_set.difference(SUPPORTED_SEARCH_PLATFORMS)
    if unsupported:
        logging.warning(
            "Ignoring unsupported query sources from Redis: %s",
            sorted(unsupported),
        )

    return [
        source
        for source in SUPPORTED_SEARCH_PLATFORMS
        if source in configured_set
    ]


async def get_allowed_query_sources() -> list[str]:
    try:
        raw_value = await redis_cache.get(QUERY_SOURCES_REDIS_KEY)
    except Exception as exc:
        logging.warning(
            "Unable to read query source configuration from Redis: %s",
            exc,
        )
        return list(SUPPORTED_SEARCH_PLATFORMS)

    return parse_allowed_query_sources(raw_value)
