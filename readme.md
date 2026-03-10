# 今日热榜 (Today's Hot Rankings)

通过爬虫采集数据，并进行可视化展示。  
Collect hot-ranking data from multiple sources and present it through a web UI.

- Spider project: <https://github.com/datehoer/hotToday>
- Website: <https://www.hotday.uk/>
- Legacy site: ~~https://hotrank.datehoer.com/~~

## Project structure

This repository currently contains:

- **Backend**: Python + FastAPI
- **Frontend (legacy)**: `ui/` — Vue 2 + Element UI + IconPark
- **Frontend (current/live)**: `vue-ui/` — Vue 3 + Vite + TypeScript + Tailwind CSS + Heroicons

> As of the current online deployment, **`https://www.hotday.uk/` is serving the `vue-ui/` frontend**.  
> The live page loads Vite-built assets such as `/assets/index-*.js` and `/assets/index-*.css`, and its DOM structure/styles match `vue-ui/src/App.vue`.

## Backend

Backend stack:

- FastAPI
- Redis
- PostgreSQL

Recent backend changes already reflected in the repo:

- **2025-03-03**
  - switched storage from MongoDB to PostgreSQL to reduce memory usage
  - added global rate limiting

### Backend deployment

After building the Docker image, you can run the backend container like this:

```bash
docker run -itd --name hotrank \
  -v /var/www/hotday.uk/feed:/app/rss_feed.xml \
  -v /var/www/hotday.uk/feed_with_ai:/app/rss_feed_today_top_news.xml \
  -v /opt/hot-rank-web/app.py:/app/app.py \
  -v /opt/hot-rank-web/parse_detail.py:/app/parse_detail.py \
  -v /opt/hot-rank-web/common.py:/app/common.py \
  -v /opt/hot-rank-web/config.py:/app/config.py \
  -p 127.0.0.1:7545:7545 \
  hotrank:v0.1
```

If you are only updating code (without adding new dependencies/files into the image), restarting the container is usually enough.

## Frontend

### Current live frontend: `vue-ui/`

Recommended commands:

```bash
cd vue-ui
pnpm install
pnpm run dev
pnpm run build
```

After `pnpm run build`, deploy the generated static files from `vue-ui/dist/` to Nginx (or your static file host).

### Legacy frontend: `ui/`

The old frontend is still kept in the repository for compatibility/reference:

```bash
cd ui
pnpm install
pnpm run serve
pnpm run build
```

If you are making changes intended for the currently deployed site, prefer working in **`vue-ui/`**.

## Screenshots

![效果图1](https://oss.datehoer.com/blog/imgs/2024120523075359-20241205230752.png)
![效果图2](https://oss.datehoer.com/blog/imgs/2024120523082101-20241205230820.png)
![效果图3](https://oss.datehoer.com/blog/imgs/2024120523084962-20241205230849.png)
![效果图4](https://oss.datehoer.com/blog/imgs/2024120523090999-20241205230909.png)
![效果图5](https://oss.datehoer.com/blog/imgs/2024120523185650-20241205231856.png)
