import redis
from config import *
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)
for item in COPYWRITING:
    redis_client.sadd("copywriting", item)