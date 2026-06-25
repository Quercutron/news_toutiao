import redis.asyncio as redis
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

#创建Redis的连接对象
redis_client=redis.Redis(
    host=REDIS_HOST,#服务器地址
    port=REDIS_PORT,#端口号
    db=REDIS_DB,#数据库编号
    decode_responses=True#是否自动将返回值解码为字符串
)

#设置缓存 和 读取（字符串 或 字典列表）
#读取（字符串）
async def get_cache(key):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"Error reading cache: {e}")
        return None

#读取（字典列表）
async def get_cache_json(key):
    try:
        data=await redis_client.get(key)
        if data:
            return await json.loads(data)#反序列化
        return None
    except Exception as e:
        print(f"Error reading cache: {e}")
        return None

#设置缓存   key: 缓存键值  value: 缓存值  expire: 缓存过期时间（秒）
async def set_cache(key,value,expire=3600):
    try:
        #如果值是字典类型，则先转换为JSON字符串
        if isinstance(value, (dict, list)):
            #将字典类型转换为JSON字符串,中文正常保存
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key,value,expire)
        return True
    except Exception as e:
        print(f"Error writing cache: {e}")
        return False

