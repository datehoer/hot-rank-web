import redis
from config import *
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)
# for item in COPYWRITING:
#     redis_client.sadd("copywriting", item)

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

texts = [
    "周だ贱伦てゆ",
    "お讉莣諾戀ぁ",
    "祗尖ベ煙Ω圈?",
    "ヤ茈情kě待",
    "﹎ì.呦児圜",
    "⑥星飛ㄚц♀",
    "⿶莳尙寳ル",
    "メㄝ界末ㄖ.",
    "┌蕝薱願創",
    "℡左掱寫愛",
    "￠伤…①⑨",
    "⺌點點頭﹎答",
    "壞壊deヤωǒ",
    "⿻?愛の终゛",
    "╰熹ゞㄡ欠﹎",
    "ジェ愛隨緣ラ",
    "☆LèLè☆",
    "5`⒋з.2.ㄧ",
    "⿴╪｛张侗學",
    "ャ⿴國際淫蕩",
    "僾伱Ъㄩ逅誨",
    "(_少鈎鈏ωǒ ゛",
    "｛｛冄坙",
    "〣咹魵點.√",
    "╭ブ簡單愛",
    "(_灬兲使ぺ",
    "㊣er㈧經de愛",
    "娓ぁ装ω",
    "尛鷄侽孖",
    "⑦穜↘菋噵◇",
    "⿺﹎單裑m^",
    "|曐⑦叭|▍",
    "♂莣鋽濄麮♀ :",
    "_瑏cuò鞋●",
    "﹌銥賴▼.",
    "︶ㄣ冰锋⺗︵",
    "溈鉨ｗǒ變乖",
    "╀絕蝂oо`倫",
    "儰你變乖",
    "獨特ω銥賴",
    "に訫隨Ｗǒ變",
    "風蓅乄無惢￠",
    "の寳唄;莉児",
    "ゞ莣鋽ど鍋佉",
    "しov聽花若北\\",
    "尐囡壞脾氣",
    "＂國際尛鷄m",
    "鶏㈧嘵yáo芓",
    "誮た尐羅卟ま",
    "咹靜嘚消失",
    "№帅馨の戀♂",
    "●勁儛娚駭ぽ",
    "鎖骨秀姿色",
    "學^ō^乖→咗",
    "⒛ō⑦緟鋅愛",
    "╰☆╮雨㊣神",
    "硪◎－◎拽oκ",
    "冰雪獨爱征",
    "ヤ寶ы.ゞ児o"
]
for text in texts:
    redis_client.sadd("username", text)
