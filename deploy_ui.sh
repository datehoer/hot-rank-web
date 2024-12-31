#!/bin/bash

# 设置路径变量 （Setting env）
UI_DIR="/opt/hot-rank-web/ui"
DIST_DIR="/opt/hot-rank-web/ui/dist"
WWW_DIR="/var/www/hotday.uk"

echo "开始部署流程..."

# 进入UI目录 (Enter UI directory)
cd $UI_DIR

# 安装依赖并构建 (Install dependencies and build)
echo "安装依赖..."
npm install

echo "构建项目..."
npm run build

# 确保构建成功 (Ensure build success)
if [ $? -ne 0 ]; then
    echo "构建失败，退出部署"
    exit 1
fi

# 复制 feed 相关文件到 dist 目录 (Copy feed files to dist directory)
echo "复制 feed 文件到 dist..."
cp $WWW_DIR/feed $DIST_DIR/ 2>/dev/null || true
cp $WWW_DIR/feed_with_ai $DIST_DIR/ 2>/dev/null || true

# 清空 www 目录 (Clear www directory)
echo "清空 www 目录..."
rm -rf $WWW_DIR/*

# 复制新的构建文件到 www 目录 (Copy new build files to www directory)
echo "部署新文件..."
cp -r $DIST_DIR/* $WWW_DIR/

# 设置权限 (Set permissions)
echo "设置权限..."
chown -R www-data:www-data $WWW_DIR
chmod -R 755 $WWW_DIR

# 检查 Nginx 配置并根据结果决定是否重载 (Check Nginx config and decide whether to reload based on the result)
echo "检查 Nginx 配置..."
if nginx -t 2>/dev/null; then
    echo "Nginx 配置检查通过，正在重新加载..."
    nginx -s reload
    echo "Nginx 重新加载完成！"
else
    echo "Nginx 配置检查失败，取消重新加载"
    exit 1
fi

echo "部署完成！"
