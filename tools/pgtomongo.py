import pymongo
import psycopg2
import json
from tqdm import tqdm
from config import *
# 连接到 MongoDB
mongo_client = pymongo.MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB_NAME]

# 连接到 PostgreSQL
pg_conn = psycopg2.connect(f"host={PG_HOST} port={PG_PORT} dbname={PG_DB} user={PG_USER} password={PG_PASSWORD}")
pg_cursor = pg_conn.cursor()

collection_names = mongo_db.list_collection_names()
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
        else:
            if "data" not in document:
                continue
            data = document['data']
        insert_time = document['insert_time']

        # 将数据插入到 PostgreSQL
        pg_cursor.execute(f'INSERT INTO "{collection_name}" (data, insert_time) VALUES (%s, %s)', (json.dumps(data), insert_time))

# 提交更改并关闭连接
pg_conn.commit()
pg_cursor.close()
pg_conn.close()
mongo_client.close()