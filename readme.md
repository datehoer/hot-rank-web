### 今日热榜 (Today's Hot Rankings)
通过爬虫采集数据，并进行可视化展示 (Data collection through web crawling and visualization display)

爬虫项目: https://github.com/datehoer/hotToday

demo: [~~原网站~~](https://hotrank.datehoer.com/) => https://www.hotday.uk/

前后端项目 (Frontend and Backend Project)：

- 前端 (Frontend): vue2 + element-ui + [iconpark图标库](https://iconpark.oceanengine.com/official)
- 后端 (Backend): python + fastapi

后端部署建议：
docker编译镜像后使用下方命令启动docker容器，之后更新代码只需要重启容器即可(在不添加新的文件/库的情况下)
~~~bash
docker run -itd --name hotrank -v /var/www/hotday.uk/feed:/app/rss_feed.xml -v /var/www/hotday.uk/feed_with_ai:/app/rss_feed_today_top_news.xml -v /opt/hot-rank-web/app.py:/app/app.py -v /opt/hot-rank-web/parse_detail.py:/app/parse_detail.py -v /opt/hot-rank-web/common.py:/app/common.py -v /opt/hot-rank-web/config.py:/app/config.py -p 127.0.0.1:7545:7545 hotrank:v0.1
~~~
前端部署建议：
npm build后将文件复制到nginx文件夹即可

目前采集平台有 (Current Collection Platforms):
- B站热榜 (Bilibili Hot Rankings)
- 抖音热搜 (Douyin Hot Search)
- 澎湃新闻 (The Paper News)
- 掘金热榜 (Juejin Hot Rankings)
- 少数派热榜 (Sspai Hot Rankings)
- 加密货币 (Cryptocurrency)
- 贴吧热议 (Tieba Hot Topics)
- 头条热榜 (Toutiao Hot Rankings)
- 微博热搜 (Weibo Hot Search)
- 知乎热榜 (Zhihu Hot Rankings)
- 虎扑社区热帖 (Hupu Community Hot Posts)
- 历史上的今天 (Today in History)
- 华尔街见闻 (Wall Street News)
- 微信阅读排行榜 (WeChat Reading Rankings)
- 36氪 (36Kr)
- 52破解热榜 (52pojie Hot Rankings)
- AcFun热榜 (AcFun Hot Rankings)
- 安全客安全快讯 (Anquanke Security News)
- 百度热搜 (Baidu Hot Search)
- 白鲸出海 (White Whale Overseas)
- CSDN热榜 (CSDN Hot Rankings)
- 电商报最新消息 (E-commerce News Latest)
- 第一财经热榜 (Yicai Hot Rankings)
- 懂车帝热搜榜 (Dongchedi Hot Search)
- 豆瓣电影排行 (Douban Movie Rankings)
- FreeBuf咨询 (FreeBuf News)
- GitHub Trending
- Google 热搜 (Google Hot Search)
- 虎嗅热文 (Huxiu Hot Articles)
- 3DM
- IT之家热榜 (IT Home Hot Rankings)
- 开眼 (Kaiyan)
- 看雪热门 (Kanxue Hot Topics)
- 宽带山热榜 (KDS Hot Rankings)
- PMCAFF精选 (PMCAFF Featured)
- 汽车之家热帖榜 (Autohome Hot Posts)
- 起点榜单 (Qidian Rankings)
- 水木社区热门话题 (SMTH Hot Topics)
- 新浪热门 (Sina Hot Topics)
- 新浪体育热门 (Sina Sports Hot Topics)
- 新浪新闻热门 (Sina News Hot Topics)
- 太平洋汽车热门 (PCauto Hot Topics)
- TapTap热门 (TapTap Hot Topics)
- 腾讯新闻热点榜 (Tencent News Hot Rankings)
- 人人都是产品经理热门 (Woshipm Hot Topics)
- ~~雪球热门 (Xueqiu Hot Topics)~~
- 易车热门 (Yiche Hot Topics)
- 优设读报 (Uisdc News)
- 游戏葡萄文章推荐 (GameGrape Article Recommendations)
- 站酷榜单 (Zcool Rankings)
- 纵横24小时畅销榜 (Zongheng 24h Bestseller Rankings)
- hacknews
- 要知
- [我的博客](https://www.datehoer.com/)
- Linuxdo
- v2ex
- nodeseed
- hostloc
- wsl
- ft
- nytimes
- bloomberg



![效果图1](https://oss.datehoer.com/blog/imgs/2024120523075359-20241205230752.png)

![效果图2](https://oss.datehoer.com/blog/imgs/2024120523082101-20241205230820.png)

![效果图3](https://oss.datehoer.com/blog/imgs/2024120523084962-20241205230849.png)

![效果图4](https://oss.datehoer.com/blog/imgs/2024120523090999-20241205230909.png)

![效果图5](https://oss.datehoer.com/blog/imgs/2024120523185650-20241205231856.png)