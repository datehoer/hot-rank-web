import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import re
import markdownify
from bs4 import BeautifulSoup
from urllib.parse import urlsplit

from hotrank.agent.safe_fetcher import safe_fetch_text, validate_source_url

async def remove_img_tags(html_content):
    if not html_content:
        return html_content
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        img.decompose()
    return str(soup)

async def parse_detail(needKnowList):
    for needKnow in needKnowList:
        if "hot_url" in needKnow:
            if "thepaper.cn" in needKnow['hot_url']:
                needKnow = await parse_pengpai(needKnow)
            elif "36kr.com" in needKnow['hot_url']:
                needKnow = await parse_36kr(needKnow)
            elif "ithome.com" in needKnow['hot_url']:
                needKnow = await parse_ithome(needKnow)
            elif "sspai.com" in needKnow['hot_url']:
                needKnow = await parse_sspai(needKnow)
            elif "wallstreetcn.com" in needKnow['hot_url']:
                needKnow = await parse_awatmt(needKnow)
    return needKnowList


async def parse_pengpai(needKnow, fetcher=safe_fetch_text):
    url = needKnow['hot_url']
    res = await fetcher(url, "pengpai")
    soup = BeautifulSoup(res, 'html.parser')
    detail = None
    for selector in (
        "div[class^='cententWrap']",
        "div[class^='index_cententWrap']",
        "div[class^='header_videoWrap'] ~ div",
    ):
        detail = soup.select_one(selector)
        if detail:
            break
    if not detail:
        return needKnow

    detail = await remove_img_tags(str(detail))
    detail = markdownify.markdownify(detail).strip()
    needKnow['content'] = detail
    return needKnow

async def parse_36kr(needKnow, fetcher=safe_fetch_text):
    url = needKnow['hot_url']
    res = await fetcher(url, "36kr")
    key = "efabccee-b754-4c"
    key = key.encode('utf-8').ljust(16, b'\0')
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_state = re.findall('window.initialState={"state":"(.*?)","isEncrypt":true}', res)[0]
    encrypted_bytes = base64.b64decode(encrypted_state)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    decrypted_bytes = unpad(decrypted_padded, AES.block_size)
    decrypted_text = decrypted_bytes.decode('utf-8')
    state_dict = json.loads(decrypted_text)
    detail = state_dict['articleDetail']['articleDetailData']['data']['widgetContent']
    detail = await remove_img_tags(detail)
    needKnow['content'] = markdownify.markdownify(detail).strip()
    return needKnow

async def parse_ithome(needKnow, fetcher=safe_fetch_text):
    url = needKnow['hot_url']
    res = await fetcher(url, "ithome")
    soup = BeautifulSoup(res, 'html.parser')
    detail = soup.select_one(".news-content")
    if detail:
        detail = str(detail)
        detail = await remove_img_tags(detail)
        detail = markdownify.markdownify(detail).strip()
        needKnow['content'] = detail
    return needKnow

async def parse_sspai(needKnow, fetcher=safe_fetch_text):
    url = needKnow['hot_url']
    res = await fetcher(url, "shaoshupai_hot")
    soup = BeautifulSoup(res, 'html.parser')
    detail = soup.select_one("div.content")
    if detail:
        detail = str(detail)
        detail = await remove_img_tags(detail)
        detail = markdownify.markdownify(detail).strip()
        needKnow['content'] = detail
    return needKnow

async def parse_awatmt(needKnow, fetcher=safe_fetch_text):
    url = validate_source_url(
        needKnow['hot_url'],
        "wallstreetcn",
    ).url
    article_id = urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", article_id):
        raise ValueError("Wallstreet article ID is invalid")
    url = f"https://api-one-wscn.awtmt.com/apiv1/content/articles/{article_id}?extract=0"
    res = await fetcher(url, "wallstreetcn")
    res_json = json.loads(res)
    detail = res_json['data']['content']
    detail = await remove_img_tags(detail)
    detail = markdownify.markdownify(detail).strip()
    needKnow['content'] = detail
    return needKnow
