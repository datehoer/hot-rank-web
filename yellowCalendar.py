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

data = {}

# 解析左侧 (class="l")
left = doc('.lunars-b .l')

# 提取 Horoscope 信息
data['left_horoscopes'] = []
left('.horoscope').each(lambda i, elem: data['left_horoscopes'].append({
    'hit': pq(elem).find('.hit').text(),
    'gz': pq(elem).find('.gz').text(),
    'zodiac': pq(elem).find('.zodiac').text(),
    'nayin': pq(elem).find('.nayin').text()
}))

# 提取 Solar 图片
data['left_solar'] = left('.solar img').attr('src')

# 提取 宜忌 (yi-ji)
data['left_yi_ji'] = [pq(a).text() for a in left('.yi-ji a').items()]

# 提取 吉神宜趋 (shen-sha)
shen_sha = {}
shen_sha['title'] = left('.shen-sha .title span').text()
shen_sha['content'] = left('.shen-sha p').text()
data['left_shen_sha'] = shen_sha

# 提取 彭祖百忌和相冲 (pz-chong)
pz_chong = {}
left('.pz-chong div').each(lambda i, elem: pz_chong.update({
    pq(elem).find('.title').text(): pq(elem).find('.text').text()
}))
data['left_pz_chong'] = pz_chong

# 提取 月名、物候、月相 (yz-wh-yx)
yz_wh_yx = []
left('.yz-wh-yx div').each(lambda i, elem: yz_wh_yx.append({
    'title': pq(elem).find('.title').text(),
    'text': pq(elem).find('.text').text(),
    'img': pq(elem).find('img').attr('src')
}))
data['left_yz_wh_yx'] = yz_wh_yx

# 解析 中间部分 (class="c")
center = doc('.lunars-b .c')

# 提取 日期信息
center_top = center('.top')
data['center_datepicker'] = center_top('.form-data #datetimepicker').val()
data['center_return_today'] = center_top('.form-a').text()

# 提取 今日幸运生肖
lucky_zodiac = {}
lucky_zodiac['animals'] = [a.text() for a in center_top('.days-info .list .text a').items()]
lucky_zodiac['title'] = center_top('.days-info .list .title').text()
data['center_lucky_zodiac'] = lucky_zodiac

# 提取 今日星座
today_constellation = {}
today_constellation['constellation'] = center_top('.days-info .list').eq(1).find('.text').text()
today_constellation['title'] = center_top('.days-info .list').eq(1).find('.title').text()
data['center_today_constellation'] = today_constellation

# 提取 日期数字
data['center_date_number'] = center_top('.days-info .su').text()

# 提取 农历日期
data['center_lunar_date'] = center_top('h4').text()

# 提取 QR Code 链接
data['center_qr_codes'] = []
center_top('.down .QRcode').each(lambda i, elem: data['center_qr_codes'].append({
    'type': pq(elem).attr('data-type'),
    'img_src': pq(elem).find('img').attr('src')
}))

# 提取 注意事项
data['center_note'] = {
    'img': center_top('.note img').attr('src'),
    'text': center_top('.note span').text()
}

# 提取 Bottom 部分信息
bottom = center('.bottom')

# 提取 财神位
data['bottom_caishen'] = []
bottom('.lunars-info.shen .list .item').each(lambda i, elem: data['bottom_caishen'].append({
    'title': pq(elem).find('.title').text(),
    'text': pq(elem).find('.text').text(),
    'link': pq(elem).attr('href')
}))

# 提取 阴阳贵神
data['bottom_yinyang_guishen'] = []
bottom('.lunars-info').eq(1).find('.list .item').each(lambda i, elem: data['bottom_yinyang_guishen'].append({
    'title': pq(elem).find('.title').text(),
    'text': pq(elem).find('.text').text()
}))

# 提取 空亡所值
data['bottom_kongwang_souzhi'] = []
bottom('.lunars-info').eq(2).find('.list .item').each(lambda i, elem: data['bottom_kongwang_souzhi'].append({
    'title': pq(elem).find('.title').text(),
    'text': pq(elem).find('.text').text()
}))

# 提取 九宫飞星
data['bottom_jiugong_feixing'] = []
bottom('.lunars-info').eq(3).find('.list .item .text').each(lambda i, elem: data['bottom_jiugong_feixing'].append(pq(elem).text()))

# 解析 右侧部分 (class="l r")
right = doc('.lunars-b .l.r')

# 提取 右侧 Horoscope 信息
data['right_horoscopes'] = []
right('.horoscope').each(lambda i, elem: data['right_horoscopes'].append({
    'hit': pq(elem).find('.hit').text(),
    'gz': pq(elem).find('.gz').text(),
    'zodiac': pq(elem).find('.zodiac').text()
}))

# 提取 Solar 图片
data['right_solar'] = right('.solar img').attr('src')

# 提取 宜忌 (yi-ji)
data['right_yi_ji'] = [pq(a).text() for a in right('.yi-ji a').items()]

# 提取 凶煞宜忌 (shen-sha)
shen_sha_right = {}
shen_sha_right['title'] = right('.shen-sha .title span').text()
shen_sha_right['content'] = right('.shen-sha p').text()
data['right_shen_sha'] = shen_sha_right

# 提取 本月胎神和今日胎神 (pz-chong)
pz_chong_right = {}
right('.pz-chong div').each(lambda i, elem: pz_chong_right.update({
    pq(elem).find('.title').text(): pq(elem).find('.text').text()
}))
data['right_pz_chong'] = pz_chong_right

# 提取 岁煞、六耀、日禄 (yz-wh-yx)
yz_wh_yx_right = []
right('.yz-wh-yx div').each(lambda i, elem: yz_wh_yx_right.append({
    'title': pq(elem).find('.title').text(),
    'text': pq(elem).find('.text').text(),
    'img': pq(elem).find('img').attr('src')
}))
data['right_yz_wh_yx'] = yz_wh_yx_right

# 输出 JSON
json_result = json.dumps(data, ensure_ascii=False, indent=4)
redis_client.set("yellowCalendar", json_result)