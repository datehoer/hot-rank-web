# 构建阶段
FROM node:lts-alpine AS builder

# 设置环境变量和国内镜像源
ENV NODE_ENV=production
RUN npm config set registry https://registry.npmmirror.com && \
    mkdir -p /app

# 设置工作目录
WORKDIR /app

# 优先复制依赖文件并安装依赖
COPY package.json package-lock.json ./
RUN npm ci && npm install -g @vue/cli-service

# 复制代码并构建
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine

# 设置环境变量
ENV NGINX_PORT=80

# 复制构建产物到 nginx 静态资源目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]