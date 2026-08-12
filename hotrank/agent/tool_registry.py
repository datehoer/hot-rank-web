SUPPORTED_SEARCH_PLATFORMS = [
    "36kr",
    "3dm",
    "52pj",
    "acfun",
    "anquanke",
    "asahi",
    "baidu_hot_search",
    "baijingchuhai",
    "bilibili_hot",
    "bloomberg",
    "coolan",
    "crypto_coin",
    "csdn",
    "dailymail",
    "dianshangbao",
    "diyicaijing",
    "dongchedi",
    "douban_movie",
    "douyin_hot",
    "dzenru",
    "fivech",
    "foxnews",
    "ft",
    "github",
    "googlenews",
    "hacknews",
    "historytoday",
    "hostloc",
    "hupu",
    "huxiu",
    "ifanr",
    "ithome",
    "jin10",
    "juejin_hot",
    "kanxue",
    "kuandaishan",
    "lemonde",
    "linuxdo",
    "mcpmarket",
    "mumsnet",
    "needknow",
    "newsau",
    "nhk",
    "nodeseek",
    "nytimes",
    "openeye",
    "pengpai",
    "qichezhijia",
    "qidian",
    "readhub",
    "rt",
    "secrss",
    "shaoshupai_hot",
    "shuimu",
    "sina",
    "sina_news",
    "steam",
    "taipingyang",
    "taptap",
    "tencent_news",
    "thehackernews",
    "tieba_topic",
    "toutiao_hot",
    "v2ex",
    "wallstreetcn",
    "weibo_hot_search",
    "woshipm",
    "wx_read_rank",
    "xueqiu",
    "yiche",
    "yna",
    "youshedubao",
    "youxiputao",
    "zhanku",
    "zongheng",
]

SUPPORTED_DETAIL_PLATFORMS = [
    "wallstreetcn",
    "36kr",
    "ithome",
    "pengpai",
    "shaoshupai_hot",
]


tools = [
    {
        "type": "function",
        "name": "get_today_news",
        "description": "获取今天的热门新闻，适合回答今日热点概览类问题。",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "返回的新闻条数，默认为 10。",
                },
            },
            "required": ["limit"],
        },
    },
    {
        "type": "function",
        "name": "get_topic_detail",
        "description": "根据热点 ID 获取该话题的正文详情和摘要。",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "topic_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "hot_topic 表中的话题 ID。",
                },
                "platform": {
                    "type": "string",
                    "enum": SUPPORTED_DETAIL_PLATFORMS,
                    "description": "话题所属平台，用于选择对应的正文解析器。",
                },
            },
            "required": ["topic_id", "platform"],

        },
    },
    {
        "type": "function",
        "name": "get_rank_data",
        "description": "根据用户问题语义检索指定平台和时间范围内的热点。",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "content": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 500,
                    "description": "需要检索的用户问题或热点主题。",
                },
                "platform": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": len(SUPPORTED_SEARCH_PLATFORMS),
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "enum": SUPPORTED_SEARCH_PLATFORMS,
                    },
                    "description": "需要检索的平台列表。",
                },
            },
            "required": ["content", "platform"],
        },
    },
]


def tools_for_query_sources(allowed_sources: list[str]) -> list[dict]:
    """Build tool definitions restricted to the configured query sources."""
    import copy

    configured_tools = copy.deepcopy(tools)
    for index, tool in enumerate(configured_tools):
        if tool.get("name") != "get_rank_data":
            continue

        if not allowed_sources:
            configured_tools.pop(index)
            break

        platform_schema = tool["parameters"]["properties"]["platform"]
        platform_schema["maxItems"] = len(allowed_sources)
        platform_schema["items"]["enum"] = list(allowed_sources)
        break

    return configured_tools
