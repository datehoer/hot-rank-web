import redis
from config import *
import json
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

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

# texts = [
#     "周だ贱伦てゆ",
#     "お讉莣諾戀ぁ",
#     "祗尖ベ煙Ω圈?",
#     "ヤ茈情kě待",
#     "﹎ì.呦児圜",
#     "⑥星飛ㄚц♀",
#     "⿶莳尙寳ル",
#     "メㄝ界末ㄖ.",
#     "┌蕝薱願創",
#     "℡左掱寫愛",
#     "￠伤…①⑨",
#     "⺌點點頭﹎答",
#     "壞壊deヤωǒ",
#     "⿻?愛の终゛",
#     "╰熹ゞㄡ欠﹎",
#     "ジェ愛隨緣ラ",
#     "☆LèLè☆",
#     "5`⒋з.2.ㄧ",
#     "⿴╪｛张侗學",
#     "ャ⿴國際淫蕩",
#     "僾伱Ъㄩ逅誨",
#     "(_少鈎鈏ωǒ ゛",
#     "｛｛冄坙",
#     "〣咹魵點.√",
#     "╭ブ簡單愛",
#     "(_灬兲使ぺ",
#     "㊣er㈧經de愛",
#     "娓ぁ装ω",
#     "尛鷄侽孖",
#     "⑦穜↘菋噵◇",
#     "⿺﹎單裑m^",
#     "|曐⑦叭|▍",
#     "♂莣鋽濄麮♀ :",
#     "_瑏cuò鞋●",
#     "﹌銥賴▼.",
#     "︶ㄣ冰锋⺗︵",
#     "溈鉨ｗǒ變乖",
#     "╀絕蝂oо`倫",
#     "儰你變乖",
#     "獨特ω銥賴",
#     "に訫隨Ｗǒ變",
#     "風蓅乄無惢￠",
#     "の寳唄;莉児",
#     "ゞ莣鋽ど鍋佉",
#     "しov聽花若北\\",
#     "尐囡壞脾氣",
#     "＂國際尛鷄m",
#     "鶏㈧嘵yáo芓",
#     "誮た尐羅卟ま",
#     "咹靜嘚消失",
#     "№帅馨の戀♂",
#     "●勁儛娚駭ぽ",
#     "鎖骨秀姿色",
#     "學^ō^乖→咗",
#     "⒛ō⑦緟鋅愛",
#     "╰☆╮雨㊣神",
#     "硪◎－◎拽oκ",
#     "冰雪獨爱征",
#     "ヤ寶ы.ゞ児o"
# ]
# for text in texts:
#     redis_client.sadd("username", text)


# copywriting = ["工作是一场马拉松,而我选择做观众。", "办公室里,键盘声此起彼伏,唯独我的鼠标在悄悄画圈。", "忙碌是一种病,我正在努力保持健康。", "生产力是个美丽的词,可惜与我无缘。", "我不是懒,我只是在等待灵感的陨石砸中我。", "工作效率就像迷路的快递,总是找不到我。", "我的职业生涯是一部喜剧,每天都在上演。", "摸鱼不是技能,是艺术。我是这个领域的毕加索。", "我的工作热情,正在休年假。", "努力工作是美德,我选择做一个快乐的罪人。",'人生最大的浪漫,莫过于在工作日做着周末的美梦。', '我不是不努力,只是努力的方向是摸鱼。', '在996的世界里，摸鱼是唯一的自由。', '工作让我贫穷，摸鱼让我富有。', '摸鱼，是对无意义工作的反抗。', '如果 工作是苦海，那摸鱼就是彼岸。', '职场生存第一法则:永远看起来很忙,实际上很闲。', '时间是海绵里的水，挤不出来就摸鱼。', '工位是舞台,我们都是演技派。', '在忙碌的间隙，摸一摸鱼，看看天。', '摸鱼，是智 慧的体现。', '人生得意须摸鱼，莫使压力空对月。', '摸鱼，是对无聊制度的反叛。', '摸鱼不是堕落，是对抗无聊的方式。', '办公室的空调,是催眠曲最好的伴奏。', '办公室政治的精髓,是把摸鱼伪装成工作。', '今天不摸鱼，明天变鲨鱼。', '最高明的摸鱼,是把摸鱼本身变成一种工作。', '当代青年，摸鱼才是正道。', '我不是懒,我是在用心感受生活的节奏。', '假装加班的艺术,是21世纪最重要的技能。', '工作让我疲惫，摸鱼 让我快乐。', '摸鱼不是偷懒，是与压力和解的方式。', '假装努力的艺术,就是在领导经过时迅速切换屏幕的手速。', '会议室是最好的休息室,谁都以为你在专心听。', '工作像山，摸鱼如水，水滴石穿。', '当奋斗成为口号，摸鱼才是真理。', '人生苦短，及时摸鱼。', '在高压下，摸鱼是自我救赎。', "泡一杯枸杞茶,摆好键盘鼠标,这就是职场版'做戏要做全套'。", '职场人的终极梦想:躺平也能涨工资。', '职场生存守则:看起来很累,实际很嗨。', '工作日过得最快的时刻,就是假装在思考的午休时光。', '在喧嚣中，摸鱼是一种宁静。', '上班时我坐在工位上,灵魂已经环游世界三圈。', '在996的世界里，摸鱼是最后的浪漫。', "会议室里最动人的风景,是所有人都在低头'记笔记'。", '当生活给你柠檬，就摸鱼吧。', '如果努力有用，那咸鱼也能翻身了。', '工作群里永远在线,心早就跑到了沙滩上。', '工作报告的精髓,是把摸鱼时间写成加班。', '摸鱼，是对抗资 本主义的武器。', '如果摸鱼也算技能,那我一定是个隐藏的天才。', '上班如同网游,摸鱼就是练级,工资就是装备。', 'DDL是催人奋进的最好鞭策,也是摸鱼的最佳借口。', '摸鱼，是对自我的善待。', '职场生存智慧:把摸鱼变成一种艺术。', '上班族的双面人生:表面极客,内心极懒。', 'PPT做得好不好不重要,放映时的表情管理最重要。', '上班最高境界:看起来很努力,实际很佛系。', '摸鱼不是目的，只是生活的调剂品。', '摸鱼一时爽，一直摸鱼一直爽。', '摸鱼，是对无聊生活的嘲讽。', 'KPI是什么?Keep Pretending Industrious(保持假装勤奋)。', '领导说要日报,我写的是小说;要周报,我写的是传记。', '如果努力有用，那还要天才干嘛？摸鱼吧！', '别人家的工资按月发,我的困意按秒涌现。', '我不是不努力,我只是把效率放在了摸鱼上。', '每个工位都是小剧场,每个上班族都是影帝。', '摸鱼，让生活多一点可能性。', '工作日最动听的声音,是下班铃声交响曲。', '最高级的摸鱼,是让人看不出你在摸鱼。', '摸鱼，让我保持理智。', "工作群的'收到'二字,是职场社交最低成本的敷衍。", '摸鱼，是一种生活态度。', '我不是偷懒,我是在用战略性休息提升工作效率。', ' 工作群最高级的静音方式,是手机调成飞行模式。', '打印机旁的发呆,是职场人最后的避难所。', '别人在忙着改变世界，而我在摸鱼。', '世界那么大，我想去看看摸鱼的地方。', '在忙碌的世界里，摸鱼是一种清醒。', '当加班成为常态，摸鱼就是革命。', "工作群的'在线'状态,是最大的谎言。", '工作太多，效率太低，不如摸鱼。', '摸鱼，是对抗焦虑的良药。', '这不是摸鱼,这是工作与生活的平衡艺术。', '人生的意义，不在于工作，而在于摸鱼。', "职场修炼手册第一条:把'正在处理'发挥到极致。", '当梦想照进现实，摸鱼就成了必需品。', '工作像一场马拉松，但我更喜欢散步。', '最成功的伪装,是让忙碌看起来那么真实。', '工作日过得慢,是因为时钟也在摸鱼。', '假装打字的艺术,是职场必修课的最后一课。', '现代职场人最大的本事,是把5分钟的工作演绎成8小时的史诗。', '老板画的饼太大，得摸条鱼消化。', '摸鱼，是给灵魂放个假。', '看似认真 工作,实则内心狂欢。', '摸鱼，是平凡生活中的小确幸。', '加班和摸鱼的区别在于:一个是被迫演戏,一个是自愿沉浸。', '领导视角:奋笔疾书;实际情况:网购狂欢。', '摸鱼，是生活的润滑剂。', '工作是为了更好地摸鱼。', '人生苦短，何必认真，不如摸鱼。', '当你无法改变世界，就摸鱼吧。', '每个假装在开会的人,都是演技派配角奖的有力竞争者。', '世界上最遥远的距离,是我坐在工位上,而我的思绪已经去了马尔代夫。', '上 班如同修行,摸鱼是最高境界的禅。', '不摸鱼，毋宁死。', '人生如戏，全靠摸鱼。', '摸鱼，让生活更有趣。']
# copywriting = [
#     "领导说要全力以赴,我选择全身以退。",
#     "工作是人生的调味料,我偏爱淡而无味。",
#     "别人在职场奔跑,我在人生沙发躺平。",
#     "我不是消极怠工,是在用沉默抗议996。",
#     "工位上的我,像一尊栩栩如生的蜡像。",
#     "打工人的双手是魔术师,总能变出各种借口。",
#     "我的工作热情,被朝九晚五消磨殆尽。",
#     "摸鱼是一门艺术,需要天赋和勇气。",
#     "工作是场马拉松,我选择做观众。",
#     "KPI像星星,看得见摸不着。",
#     "我不是不努力,只是把能量用在了摸鱼上。",
#     "工资就像初恋,总觉得不够。",
#     "上班如同修行,摸鱼是顿悟。",
#     "工作效率与工资成反比。",
#     "职场如戏,全靠演技。",
#     "会议室是最好的冥想场所。",
#     "老板的期望像气球,总是吹得太大。",
#     "我的工位是孤岛,我是岛主。",
#     "摸鱼不是懒,是对生活的思考。",
#     "工作日志上写满了'明天'。",
# ]
# for text in copywriting:
#     redis_client.sadd("copywriting", text)

# table = [
#     {"name": "B站热榜", "tablename": "bilibili_hot"},
#     {"name": "抖音热搜", "tablename": "douyin_hot"},
#     {"name": "掘金热榜", "tablename": "juejin_hot"},
#     {"name": "少数派热榜", "tablename": "shaoshupai_hot"},
#     {"name": "贴吧热议", "tablename": "tieba_topic"},
#     {"name": "头条热榜", "tablename": "toutiao_hot"},
#     {"name": "微博热搜", "tablename": "weibo_hot_search"},
#     {"name": "微信阅读排行榜", "tablename": "wx_read_rank"},
#     {"name": "知乎热榜", "tablename": "zhihu_hot_list"},
#     {"name": "3DM", "tablename": "3dm"},
#     {"name": "36氪", "tablename": "36kr"},
#     {"name": "52破解热榜", "tablename": "52pj"},
#     {"name": "AcFun热榜", "tablename": "acfun"},
#     {"name": "安全客安全快讯", "tablename": "anquanke"},
#     {"name": "百度热搜", "tablename": "baidu_hot_search"},
#     {"name": "白鲸出海", "tablename": "baijingchuhai"},
#     {"name": "CSDN热榜", "tablename": "csdn"},
#     {"name": "电商报最新消息", "tablename": "dianshangbao"},
#     {"name": "第一财经热榜", "tablename": "diyicaijing"},
#     {"name": "懂车帝热搜榜", "tablename": "dongchedi"},
#     {"name": "豆瓣电影排行", "tablename": "douban_movie"},
#     {"name": "FreeBuf咨询", "tablename": "freebuf"},
#     {"name": "GitHub Trending", "tablename": "github"},
#     {"name": "Google 热搜", "tablename": "google_search"},
#     {"name": "虎扑社区热帖", "tablename": "hupu"},
#     {"name": "虎嗅热文", "tablename": "huxiu"},
#     {"name": "IT之家热榜", "tablename": "ithome"},
#     {"name": "开眼", "tablename": "openeye"},
#     {"name": "看雪热门", "tablename": "kanxue"},
#     {"name": "宽带山热榜", "tablename": "kuandaishan"},
#     {"name": "PMCAFF精选", "tablename": "pmcaff"},
#     {"name": "汽车之家热帖榜", "tablename": "qichezhijia"},
#     {"name": "起点榜单", "tablename": "qidian"},
#     {"name": "水木社区热门话题", "tablename": "shuimu"},
#     {"name": "新浪热门", "tablename": "sina"},
#     {"name": "新浪体育热门", "tablename": "sina_sport"},
#     {"name": "新浪新闻热门", "tablename": "sina_news"},
#     {"name": "太平洋汽车热门", "tablename": "taipingyang"},
#     {"name": "TapTap热门", "tablename": "taptap"},
#     {"name": "腾讯新闻热点榜", "tablename": "tencent_news"},
#     {"name": "人人都是产品经理热门", "tablename": "woshipm"},
#     {"name": "雪球热门", "tablename": "xueqiu"},
#     {"name": "易车热门", "tablename": "yiche"},
#     {"name": "优设读报", "tablename": "youshedubao"},
#     {"name": "游戏葡萄文章推荐", "tablename": "youxiputao"},
#     {"name": "站酷榜单", "tablename": "zhanku"},
#     {"name": "纵横24小时畅销榜", "tablename": "zongheng"}
# ]
# redis_client.set("card_table", json.dumps(table))

# online_movies = [{
#     "name": "播剧影视网",
#     "url": "https://www.boju.cc/"
# },{
#     "name": "Lemo",
#     "url": "https://lemo.us.kg/"
# },{"name": "555电影", "url": "https://www.55flix.com/"},
#     {"name": "低端影视", "url": "https://ddys.pro/"},
#     {"name": "LIBVIO", "url": "https://www.libvio.pro/"},
#     {"name": "热播之家", "url": "https://rebozj.pro/"},
#     {"name": "蛋蛋赞影院", "url": "https://www.dandanzan.club/"},
#     {"name": "大师兄影视", "url": "https://dsxys.pro/"},
#     {"name": "楓林網", "url": "https://imaple8.co/"},
#     {"name": "Gimy 劇迷", "url": "https://gimy.im/"},
#     {"name": "Gimy小鴨影音", "url": "https://gimy.cc/"},
#     {"name": "94i影城", "url": "https://94itv.app/"},
#     {"name": "Vidhub视频库", "url": "https://vidhub.tv/"},
#     {"name": "厂长资源", "url": "https://www.czzy77.com/"},
#     {"name": "HDmoli", "url": "https://www.hdmoli.pro/"},
#     {"name": "电影先生", "url": "https://dyxs39.com/"},
#     {"name": "4k影视", "url": "https://www.4kvm.net/"},
#     {"name": "美柏影视", "url": "https://www.mp4br.com/"},
#     {"name": "素白白影视", "url": "https://www.subaibaiys.com/"},
#     {"name": "OK电影院", "url": "https://www.okdyy.com/"},
#     {"name": "奈飞中文影视", "url": "https://netfly.fun/"},
#     {"name": "毒舌电影", "url": "https://www.duse1.com/"},
#     {"name": "胖虎免费svip影视", "url": "https://www.phyt.net/"},
#     {"name": "五五短剧", "url": "https://www.duanju55.com/"},
#     {"name": "短剧网", "url": "https://www.duanju001.com/"},
#     {"name": "短剧搜索", "url": "https://www.kdocs.cn/l/cp1MFwlimAAm?R=L1MvMQ=="},
#     {"name": "红果短剧", "url": "https://novelquickapp.com/hongguo"},
#     {"name": "全民短剧", "url": "https://playlet.kuwo.cn/"},
#     {"name": "短剧狗", "url": "https://duanjugou.top/"}
# ]

# for movie in online_movies:
#     redis_client.sadd("online_movies", json.dumps(movie))

music_list =[
    {
        'id': 1,
        'title': 'Take Me To Your Heart',
        'cover': "https://oss.datehoer.com/music/cover/TakeMeToYourHeart.jpg",
        'url': "https://oss.datehoer.com/music/mp3/TakeMeToYourHeart.m4a"
    },
    {
        'id': 2,
        'title': 'I Really Like You',
        'cover': "https://oss.datehoer.com/music/cover/ireallylikeyou.jpg",
        'url': "https://oss.datehoer.com/music/mp3/IReallyLikeYou.m4a"
    },
    {
        'id': 3,
        'title': 'APT.',
        'cover': "https://oss.datehoer.com/music/cover/APT.jpg",
        'url': "https://oss.datehoer.com/music/mp3/APT.m4a"
    },
    {
        'id': 4,
        'title': 'I Really Like You',
        'cover': "https://oss.datehoer.com/music/cover/FeelLikeANumber.jpg",
        'url': "https://oss.datehoer.com/music/mp3/FeelLikeANumber.mp3"
    }
]
for music in music_list:
    redis_client.sadd("music", json.dumps(music))

