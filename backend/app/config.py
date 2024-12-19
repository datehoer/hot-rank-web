# # MongoDB 配置
# MONGODB_URI = "mongodb://mongodb:27017"
# MONGODB_DB_NAME = "hotrankdb"

# # Redis 配置
# REDIS_HOST = 'redis'
# REDIS_PORT = 6379
# REDIS_DB = 0
# REDIS_PASSWORD = 'your_redis_password'

# news_sites = [
#     "澎湃新闻",
#     "36氪",
#     "IT之家热榜",
#     "少数派热榜",
#     "华尔街见闻"
# ]

# # 邮件配置
# EMAIL = {
#     "host": "smtp.gmail.com",
#     "port": 587,
#     "user": "your_email@gmail.com",
#     "password": "your_email_password"
# }

# # OpenAI API 配置
# OPENAI_API_KEY = "sk-36c23b81ed2f40ea861268c78c60d997"
# OPENAI_BASE_URL = "https://api.deepseek.com/v1/chat/completions"

# api_headers = {
#     "Authorization": f"Bearer {OPENAI_API_KEY}",
#     "Accept": "application/json",
#     "Content-Type": "application/json"
# }
import os
from typing import List

# MongoDB 配置
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/data?authSource=admin")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "data")

# Redis 设置
REDIS_HOST = os.getenv("REDIS_HOST", '127.0.0.1')
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# 新闻站点列表
news_sites: List[str] = [
    "澎湃新闻",
    "36氪",
    "IT之家热榜",
    "少数派热榜",
    "华尔街见闻"
]

# 邮件配置
EMAIL = {
    "host": os.getenv("EMAIL_HOST", ""),
    "port": int(os.getenv("EMAIL_PORT", "")),
    "user": os.getenv("EMAIL_USER", ""),
    "password": os.getenv("EMAIL_PASSWORD", "")
}

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-aaaaaaaaaaa")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

api_url = OPENAI_BASE_URL
api_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}