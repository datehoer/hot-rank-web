import pymongo
import psycopg2
import json
from tqdm import tqdm
# 连接到 MongoDB
mongo_client = pymongo.MongoClient("mongodb://root:JIwb158.@localhost:27017/")
mongo_db = mongo_client["hotday"]
mongo_collection = mongo_db["your_collection"]

# 连接到 PostgreSQL
pg_conn = psycopg2.connect("dbname=postgres user=admin password=securepassword")
pg_cursor = pg_conn.cursor()
collection_names = [
    "acfun",
    "openeye",
    "tencent_news",
    "woshipm",
    "wx_read_rank",
    "zongheng",
]
# 从 MongoDB 中读取数据
for collection_name in tqdm(collection_names):
    mongo_collection = mongo_db[collection_name]

    # 创建 PostgreSQL 中的表（如果不存在）
    # 需要加引号，如果是数字开头的表可以识别
    pg_cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS "{collection_name}" (
        id SERIAL PRIMARY KEY,
        data JSONB,
        insert_time BIGINT
    )
    """)

    # 从 MongoDB 中读取数据并插入到 PostgreSQL
    for document in tqdm(mongo_collection.find()):
        if collection_name == "acfun":
            data = document['rankList']
        elif collection_name == "openeye":
            data = document['result']
        elif collection_name == "tencent_news":
            data = document['idlist']
        elif collection_name == "woshipm":
            data = document['RESULT']
        elif collection_name == "wx_read_rank":
            data = document['books']
        elif collection_name == "zongheng":
            data = document['result']
        insert_time = document['insert_time']

        # 将数据插入到 PostgreSQL
        pg_cursor.execute(f'INSERT INTO "{collection_name}" (data, insert_time) VALUES (%s, %s)', (json.dumps(data), insert_time))

# 提交更改并关闭连接
pg_conn.commit()
pg_cursor.close()
pg_conn.close()
mongo_client.close()