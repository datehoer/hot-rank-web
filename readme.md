### 今日热榜 (Today's Hot Rankings)
通过爬虫采集数据，并进行可视化展示 (Data collection through web crawling and visualization display)

爬虫项目(spider project): https://github.com/datehoer/hotToday

demo: [~~原网站~~](https://hotrank.datehoer.com/) => https://www.hotday.uk/

前后端项目 (Frontend and Backend Project)：

- 前端 (Frontend): vue2 + element-ui + [iconpark图标库](https://iconpark.oceanengine.com/official)
- 后端 (Backend): python + fastapi

后端部署建议(Backend Deployment Recommendations)：

docker编译镜像后使用下方命令启动docker容器，之后更新代码只需要重启容器即可(在不添加新的文件/库的情况下)

After building the Docker image, use the command below to start the Docker container. Afterward, updating the code only requires restarting the container (as long as you are not adding new files or libraries).

~~~bash
docker run -itd --name hotrank -v /var/www/hotday.uk/feed:/app/rss_feed.xml -v /var/www/hotday.uk/feed_with_ai:/app/rss_feed_today_top_news.xml -v /opt/hot-rank-web/app.py:/app/app.py -v /opt/hot-rank-web/parse_detail.py:/app/parse_detail.py -v /opt/hot-rank-web/common.py:/app/common.py -v /opt/hot-rank-web/config.py:/app/config.py -p 127.0.0.1:7545:7545 hotrank:v0.1
~~~
前端部署建议(Frontend Deployment Recommendations)：
npm build后将文件复制到nginx文件夹即可
After running npm build, copy the resulting files to the Nginx directory.

![效果图1](https://oss.datehoer.com/blog/imgs/2024120523075359-20241205230752.png)

![效果图2](https://oss.datehoer.com/blog/imgs/2024120523082101-20241205230820.png)

![效果图3](https://oss.datehoer.com/blog/imgs/2024120523084962-20241205230849.png)

![效果图4](https://oss.datehoer.com/blog/imgs/2024120523090999-20241205230909.png)

![效果图5](https://oss.datehoer.com/blog/imgs/2024120523185650-20241205231856.png)