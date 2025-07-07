import aiohttp
import json
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import re
import markdownify
from bs4 import BeautifulSoup

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


async def fetch(url):
    timeout = aiohttp.ClientTimeout(total=360.0)
    async with aiohttp.ClientSession(timeout=timeout) as client:
        async with client.get(url) as response:
            return await response.text()


async def parse_pengpai(needKnow):
    url = needKnow['hot_url']
    res = await fetch(url)
    soup = BeautifulSoup(res, 'html.parser')
    try:
        detail = soup.select_one("div[class^='index_cententWrap']")
        if not detail:
            detail = soup.select_one("div[class^='header_videoWrap'] ~ div")
        if detail:
            detail = str(detail)
    except:
        return needKnow
    detail = await remove_img_tags(detail)
    detail = markdownify.markdownify(detail).strip()
    needKnow['content'] = detail
    return needKnow

async def parse_36kr(needKnow):
    url = needKnow['hot_url']
    res = await fetch(url)
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

async def parse_ithome(needKnow):
    url = needKnow['hot_url']
    res = await fetch(url)
    soup = BeautifulSoup(res, 'html.parser')
    detail = soup.select_one(".news-content")
    if detail:
        detail = str(detail)
        detail = await remove_img_tags(detail)
        detail = markdownify.markdownify(detail).strip()
        needKnow['content'] = detail
    return needKnow

async def parse_sspai(needKnow):
    url = needKnow['hot_url']
    res = await fetch(url)
    soup = BeautifulSoup(res, 'html.parser')
    detail = soup.select_one("div.content")
    if detail:
        detail = str(detail)
        detail = await remove_img_tags(detail)
        detail = markdownify.markdownify(detail).strip()
        needKnow['content'] = detail
    return needKnow

async def parse_awatmt(needKnow):
    url = needKnow['hot_url']
    artile_id = url.split("?")[0].split("/")[-1]
    url = f"https://api-one-wscn.awtmt.com/apiv1/content/articles/{artile_id}?extract=0"
    res = await fetch(url)
    res_json = json.loads(res)
    detail = res_json['data']['content']
    detail = await remove_img_tags(detail)
    detail = markdownify.markdownify(detail).strip()
    needKnow['content'] = detail
    return needKnow