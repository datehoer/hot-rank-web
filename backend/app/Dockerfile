# 使用更轻量级的基础镜像
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    PYTHONPATH=/app

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY . /app

# 使用清华源更新系统并安装必要依赖
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包，使用清华镜像源
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    fastapi \
    uvicorn[standard] \
    motor \
    redis \
    pydantic \
    pyquery \
    httpx \
    feedgen \
    json-repair \
    pycryptodome \
    beautifulsoup4 \
    markdownify \
    pydantic[email]

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    curl_cffi \
    pyquery \
    redis

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["sh", "-c", "python pushSomethingTask.py && python pushSomethings.py && uvicorn app:app --host 0.0.0.0 --port 8000"]