import datetime
import json
from idlelib import autocomplete_w
from typing import Any

import redis.asyncio as redis
#redis内置了异步功能，直接pip install redis 即可
#创建1个redis的连接对象
from dotenv import load_dotenv
import os
load_dotenv(override=True)
REDIS_HOST=os.getenv("ASYNC_DB_URL")
REDIS_PORT=os.getenv("ASYNC_DB_URL")
REDIS_DB=os.getenv("ASYNC_DB_URL")
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,#1个redis实例提供16个逻辑数据库编号0-15
    password=None,
    decode_responses=True#是否将字节数据解码为字符串

)
#设置和读取（字符串 、列表、字典）
#读取字符串
async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败{e}")
        return None
#读取列表、字典
async def get_json_cache(key:str):
    try:
        data= await redis_client.get(key)
        if data:
            return json.loads(data)#序列化
        return None
    except Exception as e:
        print(f"获取JSON缓存失败{e}")
        return None
#设置缓存
async def set_cache(key:str, value:Any, expire: int=3600):
    try:
        if isinstance(value,(dict,list)):
            #转字符再存进去
            value = json.dumps(value,ensure_ascii=False)#设置中文正常保存
        await redis_client.setex(key,expire,value)
        return True
    except Exception as e:
        print(f"设置缓存失败{e}")
        return False
