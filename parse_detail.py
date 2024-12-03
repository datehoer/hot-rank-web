import httpx
import json
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import pyquery
import base64
import re
async def parse_detail(needKnowList):
    for needKnow in needKnowList:
        if "thepaper.cn" in needKnow['hot_url']:
            needKnow = await parse_pengpai(needKnow)
        elif "36kr.com" in needKnow['hot_url']:
            needKnow = await parse_36kr(needKnow)
    return needKnowList


async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text


async def parse_pengpai(needKnow):
    url = needKnow['hot_url']
    res = await fetch(url)
    pq = pyquery.PyQuery(res)
    detail = pq("h1~div").text()
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
    needKnow['content'] = state_dict['articleDetail']['articleDetailData']['data']['widgetContent']
    return needKnow

async def main():
    # 测试数据
    test_data = [
        {
            'hot_url': 'https://www.36kr.com/p/3061699221143300',
            'title': 'Test Article 1'
        },
        {
            'hot_url': 'https://www.36kr.com/p/3062989680862336',
            'title': 'Test Article 2'
        }
    ]
    
    
    results = await parse_detail(test_data)
    
    
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Content: {result['content'][:100]}...")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())