#!/bin/bash
set -e

CONTAINER_NAME="hotrank"
IMAGE_NAME="hotrank"
IMAGE_TAG="v0.1"

# 停止并删除容器（如果存在）
if docker ps -a --format '{{.Names}}' | grep -wq "$CONTAINER_NAME"; then
    echo "$CONTAINER_NAME 容器存在，正在删除..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
else
    echo "$CONTAINER_NAME 容器不存在"
fi

# 删除镜像（如果存在）
if docker images --format '{{.Repository}}:{{.Tag}}' | grep -wq "$IMAGE_NAME:$IMAGE_TAG"; then
    echo "$IMAGE_NAME:$IMAGE_TAG 镜像存在，正在删除..."
    docker rmi "$IMAGE_NAME:$IMAGE_TAG"
else
    echo "$IMAGE_NAME:$IMAGE_TAG 镜像不存在"
fi

# 重新构建镜像
echo "开始构建镜像..."
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

echo "镜像构建完成"