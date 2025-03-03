FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

WORKDIR /app
COPY pushSomethingTask.py /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    curl_cffi \
    pyquery \
    redis

EXPOSE 7545

CMD ["python", "pushSomethingTask.py"]
