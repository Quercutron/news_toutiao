from typing import List, Dict, Any, Optional

from config.cache_config import get_cache_json, set_cache

#封装新闻相关的缓存方法：新闻分类的读取和缓存
CATEGORIES_KEY="news:categories"
NEWS_LIST_PROFIX="news_list:"

#获取新闻分类缓存
async def get_news_categories_cache():
    return await get_cache_json(CATEGORIES_KEY)

#写入新闻分类缓存
async def set_news_categories_cache(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)

#写入新闻缓存
#redis:库名：key:news_list:分类id:页码：每页数量 +列表数据+缓存过期时间
async def set_news_list_cache(category_id: Optional[int], page: int, size: int, data: List[Dict[str, Any]], expire: int = 1200):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PROFIX}{category_part}:{page}:{size}"
    return await set_cache(key, data, expire)

#获取新闻缓存
async def get_news_list_cache(category_id: Optional[int], page: int, size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PROFIX}{category_part}:{page}:{size}"
    return await get_cache_json(key)


