import math
from urllib.parse import urljoin
def parse_douyin_hot(data):
    data = data["data"]['word_list']
    result = []
    for item in data:
        hot_value = int(item["hot_value"])
        hot_label = item["word"]
        hot_url = "https://www.douyin.com/search/" + hot_label
        result.append({
            "hot_value": hot_value,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_bilibili_hot(data):
    data = data["data"]['list']
    result = []
    w1, w2, w3, w4, w5, w6, w7 = 0.1, 0.3, 0.5, 0.4, 0.6, 0.4, 0.3
    for item in data:
        state = item['stat']
        view = int(state['view'])
        danmaku = int(state['danmaku'])
        reply = int(state['reply'])
        favorite = int(state['favorite'])
        coin = int(state['coin'])
        share = int(state['share'])
        like = int(state['like'])
        hot_value = (view * w1 + danmaku * w2 + reply * w3 +
                favorite * w4 + coin * w5 + share * w6 + like * w7)
        hot_url = item["short_link_v2"]
        hot_label = item["title"]
        result.append({
            "hot_value": math.floor(hot_value),
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_juejin_hot(data):
    data = data["data"]['data']
    result = []
    for item in data:
        hot_value = int(item['content_counter']['hot_rank'])
        hot_url = "https://juejin.cn/post/" + str(item["content"]["content_id"])
        hot_label = item["content"]['title']
        result.append({
            "hot_value": hot_value,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_shaoshupai_hot(data):
    data = data["data"]
    result = []
    for item in data:
        comment_count = int(item["comment_count"])
        like_count = int(item["like_count"])
        hot_value = comment_count*0.6 + like_count*0.3
        hot_url = "https://sspai.com/post/" + str(item["id"])
        hot_label = item["title"]
        result.append({
            "hot_value": math.floor(hot_value),
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_tieba_topic(data):
    data = data["data"]["data"]['bang_topic']['topic_list']
    result = []
    for item in data:
        hot_value = int(item["discuss_num"])
        hot_url = item["topic_url"]
        hot_label = item["topic_name"]
        result.append({
            "hot_value": hot_value,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_toutiao_hot(data):
    data = data["data"]["data"]
    result = []
    for item in data:
        hot_value = int(item["HotValue"])
        hot_url = item["Url"]
        hot_label = item["Title"]
        result.append({
            "hot_value": hot_value,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_weibo_hot_search(data):
    data = data["data"]["data"]['cards'][0]['card_group']
    result = []
    for item in data:
        hot_url = item["scheme"]
        hot_label = item["desc"]
        result.append({
            "hot_value": 0,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    return result

def parse_wx_read_rank(data):
    data = data["data"]["books"]
    result = []
    for item in data:
        hot_label = item["bookInfo"]["title"]
        hot_value = int(item['readingCount'])
        result.append({
            "hot_value": hot_value,
            "hot_url": "",
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_zhihu_hot_list(data):
    data = data["data"]["data"]
    result = []
    for item in data:
        hot_value = 0
        try:
            hot_value = float(item["detail_text"].split(" ")[0])*10000
        except:
            pass
        if item['target']['type'] == "question":
            hot_url = "https://www.zhihu.com/question/" + str(item['target']['id'])
        else:
            continue
        hot_label = item['target']['title']
        result.append({
            "hot_value": hot_value,
            "hot_url": hot_url,
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_common(data):
    result = []
    data = data['data']
    is_percent = False
    for item in data:
        hot_value = item.get("hotScore")
        if isinstance(hot_value, str):
            if "%" in hot_value:
                is_percent = True
            else:
                hot_value = float(hot_value.replace("热度", '').replace("万", "0000"))
        if not is_percent:
            hot_value = math.floor(hot_value)
        result.append({
            "hot_value": hot_value,
            "hot_url": item['url'],
            "hot_label": item['title']
        })
    if not is_percent:
        result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_anquanke(data):
    result = []
    data = data['data']['list']
    for item in data:
        result.append({
            "hot_value": 0,
            "hot_url": urljoin("https://www.anquanke.com", item['url']),
            "hot_label": item['title']
        })
    return result

def parse_acfun(data):
    data = data['data']
    result = []
    for item in data:
        result.append({
            "hot_value": 0,
            "hot_url": item['shareUrl'],
            "hot_label": item['title']
        })
    return result

def parse_csdn(data):
    data = data['data']
    result = []
    for item in data:
        result.append({
            "hot_value": item['hotRankScore'],
            "hot_url": item['articleDetailUrl'],
            "hot_label": item['articleTitle']
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_douban(data):
    data = data['data']
    koubei = parse_common(data[0])
    beimei = parse_common(data[1])
    return koubei, beimei

def parse_openeye(data):
    result = []
    items = data.get("data", [])
    for item in items.get("card_list", []):
        metro_list = item['card_data']['body'].get('metro_list', [])
        for metro in metro_list:
            title = metro['metro_data'].get('title', "")
            if title == "":
                continue
            link = metro['link']
            hotScore = metro['metro_data']['hot_value']
            result.append({
                "hot_label": title,
                "hot_url": link,
                "hot_value": hotScore
            })
    return result

def parse_pmcaff(data):
    result = []
    results = data['data']
    for res in results:
        title = res['title']
        link = res['shareUrl']
        hotScore = res['viewNum']
        result.append({
            'hot_label': title,
            'hot_url': link,
            'hot_value': hotScore,
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_woshipm(data):
    results = data.get('data', [])
    result = []
    for res in results:
        result_data = res['data']
        title = result_data['articleTitle']
        link = "https://www.woshipm.com/{}/{}.html".format(result_data['type'], result_data['id'])
        hotScore = res['scores']
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hotScore
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_xueqiu(data):
    import pyquery
    result = []
    for i in data.get("items", []):
        original = i['original_status']
        title = original['description']
        doc = pyquery.PyQuery(title)
        title = doc.text()[0:60]
        link = urljoin("https://xueqiu.com", original['target'])
        hotScore = 0
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hotScore
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_yiche(data):
    article_res_json = data['data']
    result = []
    for res in article_res_json:
        title = res['shareData']['title']
        link = res['shareData']['link']
        hotScore = 0
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hotScore
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_youshedubao(data):
    uisdc_news = data['data'][0]['dubao']
    result = []
    for news in uisdc_news:
        title = news['title']
        result.append({
            "hot_label": title,
            "hot_url": "https://www.uisdc.com/news",
            "hot_value": 0
        })
    return result

def parse_youxiputao(data):
    res_json = data['data']
    result = []
    for item in res_json['data']:
        title = item["title"]
        link = "https://youxiputao.com/article/" + str(item['id'])
        hotScore = 0
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hotScore
        })
    return result

def parse_zhanku(data):
    result = []
    results = data['data']
    for res in results:
        title = res['rankingTitle']
        link = res['pageUrl']
        hotScore = res['rankScore']
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hotScore
        })
    return result

def parse_zongheng(data):
    result = []
    for item in data.get("data", {}).get("resultList", []):
        result.append({
            "hot_label": item.get("bookName"),
            "hot_url": "https://www.zongheng.com/detail/{}".format(item.get("bookId")),
            "hot_value": 0
        })
    return result

def parse_tencent_news(data):
    data = data['data'][0]['newslist']
    result = []
    for item in data:
        if not item.get('url'):
            continue
        comment_count = int(item.get('commentNum', 0))
        read_count = int(item.get('readCount', 0))
        collect_count = int(item.get('collectCount', 0))
        hot_value = comment_count*0.6 + read_count*0.3 + collect_count*0.1
        result.append({
            "hot_label": item['title'],
            "hot_url": item['url'],
            "hot_value": math.floor(hot_value)
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result


def parse_hupu(data):
    data = data['data']
    result = []
    for item in data:
        try:
            hot_label = item['title'].encode('ISO-8859-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            hot_label = item['title']
        result.append({
            "hot_value": item['hotScore'],
            "hot_url": item['url'],
            "hot_label": hot_label
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_coolan(data):
    data = data['data']
    result = []
    for item in data:
        title = item.get('title')
        if not title:
            continue
        url = "https://www.coolapk.com" + item['turl']
        hot_value = item['rank_score']
        result.append({
            "hot_value": hot_value,
            "hot_url": url,
            "hot_label": title
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_wallstreetcn(data):
    data = data['data']['day_items']
    result = []
    for item in data:
        title = item['title']
        link = item['uri']
        hot_value = item['pageviews']
        result.append({
            "hot_label": title,
            "hot_url": link,
            "hot_value": hot_value
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result

def parse_pengpai(data):
    data = data['data']['hotNews']
    result = []
    for item in data:
        result.append({
            "hot_label": item['name'],
            "hot_url": "https://www.thepaper.cn/newsDetail_forward_" +item['contId'],
            "hot_value": 0
        })
    return result

def parse_linuxdo(data):
    data = data['data']
    result = []
    weight_posts = 1.0
    weight_replies = 1.5
    weight_views = 0.5
    weight_likes = 2.0
    for item in data:
        posts_count = item.get("posts_count", 0)
        reply_count = item.get("reply_count", 0)
        views_count = item.get("views", 0)
        like_count = item.get("like", 0)
        heat_score = (
            weight_posts * posts_count +
            weight_replies * reply_count +
            weight_views * math.log(views_count + 1) +
            weight_likes * like_count
        )
        result.append({
            "hot_label": item['title'],
            "hot_url": "https://linux.do/t/topic/" + str(item['id']),
            "hot_value": math.floor(heat_score)
        })
    result.sort(key=lambda x: x["hot_value"], reverse=True)
    return result