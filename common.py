import math
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
    data = data["data"]
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
    data = data["data"]['bang_topic']['topic_list']
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
    data = data["data"]
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
    data = data["data"]['cards'][0]['card_group']
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
    data = data["books"]
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
    data = data["data"]
    result = []
    for item in data:
        hot_value = float(item["detail_text"].split(" ")[0])*10000
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