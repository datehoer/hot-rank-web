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
    url = "https://www.huangli.com/"
    html_content = requests.get(url).text
    doc = pq(html_content)
    data = {}

    # 解析左侧部分
    left = doc('.lunars-b .l')

    # 提取左侧 Horoscope 信息
    data['left_horoscopes'] = []
    for elem in left('.horoscope').items():
        data['left_horoscopes'].append({
            'hit': elem.find('.hit').text(),
            'gz': elem.find('.gz').text(),
            'zodiac': elem.find('.zodiac').text(),
            'nayin': elem.find('.nayin').text()
        })

    # 提取左侧 Solar 图片
    data['left_solar'] = left('.solar img').attr('src')

    # 提取左侧宜忌
    data['left_yi_ji'] = [a.text() for a in left('.yi-ji').eq(0).find('a').items()]

    # 提取左侧吉神宜趋
    data['left_shen_sha'] = {
        'title': left('.shen-sha .title span').text(),
        'content': left('.shen-sha p').text()
    }

    # 提取左侧彭祖百忌和相冲
    pz_chong = {}
    for elem in left('.pz-chong div').items():
        title = elem.find('.title').text()
        text = elem.find('.text').text()
        pz_chong[title] = text
    data['left_pz_chong'] = pz_chong

    # 提取左侧月名、物候、月相
    yz_wh_yx = []
    for elem in left('.yz-wh-yx div').items():
        yz_wh_yx.append({
            'title': elem.find('.title').text(),
            'text': elem.find('.text').text(),
            'img': elem.find('img').attr('src')
        })
    data['left_yz_wh_yx'] = yz_wh_yx

    # 解析中间部分
    center = doc('.lunars-b .c')
    center_top = center('.top')

    # 提取日期信息
    data['center_datepicker'] = center_top('.form-data #datetimepicker').val()
    data['center_return_today'] = center_top('.form-a').text()

    # 提取今日幸运生肖
    lucky_zodiac = {
        'animals': [a.text() for a in center_top('.days-info .list').eq(0).find('.text a').items()],
        'title': center_top('.days-info .list').eq(0).find('.title').text()
    }
    data['center_lucky_zodiac'] = lucky_zodiac

    # 提取今日星座
    today_constellation = {
        'constellation': center_top('.days-info .list').eq(1).find('.text').text(),
        'title': center_top('.days-info .list').eq(1).find('.title').text()
    }
    data['center_today_constellation'] = today_constellation

    # 提取日期数字和农历日期
    data['center_date_number'] = center_top('.days-info .su').text()
    data['center_lunar_date'] = center_top('h4').text()

    # 提取二维码链接
    data['center_qr_codes'] = []
    for elem in center_top('.down .QRcode').items():
        data['center_qr_codes'].append({
            'type': elem.attr('data-type'),
            'img_src': elem.find('img').attr('src')
        })

    # 提取注意事项
    data['center_note'] = {
        'img': center_top('.note img').attr('src'),
        'text': center_top('.note span').text()
    }

    # 提取底部信息
    bottom = center('.bottom')

    # 提取财神位
    data['bottom_caishen'] = []
    for elem in bottom('.lunars-info.shen .list .item').items():
        data['bottom_caishen'].append({
            'title': elem.find('.title').text(),
            'text': elem.find('.text').text(),
            'link': elem.attr('href')
        })

    # 提取阴阳贵神
    data['bottom_yinyang_guishen'] = []
    for elem in bottom('.lunars-info').eq(1).find('.list .item').items():
        data['bottom_yinyang_guishen'].append({
            'title': elem.find('.title').text(),
            'text': elem.find('.text').text()
        })

    # 提取空亡所值
    data['bottom_kongwang_souzhi'] = []
    for elem in bottom('.lunars-info').eq(2).find('.list .item').items():
        data['bottom_kongwang_souzhi'].append({
            'title': elem.find('.title').text(),
            'text': elem.find('.text').text()
        })

    # 提取九宫飞星
    data['bottom_jiugong_feixing'] = [
        elem.text() for elem in bottom('.lunars-info').eq(3).find('.list .item .text').items()
    ]

    # 解析右侧部分
    right = doc('.lunars-b .l.r')

    # 提取右侧 Horoscope 信息
    data['right_horoscopes'] = []
    for elem in right('.horoscope').items():
        data['right_horoscopes'].append({
            'hit': elem.find('.hit').text(),
            'gz': elem.find('.gz').text(),
            'zodiac': elem.find('.zodiac').text()
        })

    # 提取右侧 Solar 图片
    data['right_solar'] = right('.solar img').attr('src')

    # 提取右侧宜忌
    data['right_yi_ji'] = [a.text() for a in right('.yi-ji a').items()]

    # 提取右侧凶煞宜忌
    data['right_shen_sha'] = {
        'title': right('.shen-sha .title span').text(),
        'content': right('.shen-sha p').text()
    }

    # 提取右侧本月胎神和今日胎神
    pz_chong_right = {}
    for elem in right('.pz-chong div').items():
        title = elem.find('.title').text()
        text = elem.find('.text').text()
        pz_chong_right[title] = text
    data['right_pz_chong'] = pz_chong_right

    # 提取右侧岁煞、六耀、日禄
    yz_wh_yx_right = []
    for elem in right('.yz-wh-yx div').items():
        yz_wh_yx_right.append({
            'title': elem.find('.title').text(),
            'text': elem.find('.text').text(),
            'img': elem.find('img').attr('src')
        })
    data['right_yz_wh_yx'] = yz_wh_yx_right

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
