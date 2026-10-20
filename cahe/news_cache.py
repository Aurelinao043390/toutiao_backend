#新闻相关的缓存方法：新闻分类的读取和写入
from typing import List, Dict, Any, Optional

from config.cache_config import redis_client, get_json_cache, set_cache

CATEGORY_KEY="news:categories"
NEWS_LIST_PREFIX="news_list"
#获取新闻分类的缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORY_KEY)

#写入新闻分类缓存：缓存的数据 和 过期的时间
#配置 分类7200  详情1800 列表600 验证吗码120 总之数据越稳定，缓存越持久
async def set_cache_categories(data:List[Dict[str,Any]],expire: int=7200):
    return await set_cache(CATEGORY_KEY, data, expire)
#定义新闻列表的写入缓存的方法、
#key的唯一性news_list:分类id：页码：每页数量
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,news_list:List[str,Any],expire:int=1800):
    category_part= category_id if category_id is not None else "all"
    key=f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await set_cache(key,news_list,expire)
#定义新闻列表的读取缓存的方法
async def get_cached_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await get_json_cache(key)