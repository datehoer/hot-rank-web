FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
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
    pydantic[email] \
    slowapi

EXPOSE 7545

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7545"]
