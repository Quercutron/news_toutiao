from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache_news import get_news_categories_cache, set_news_categories_cache, get_news_list_cache, \
    set_news_list_cache
from models.news import Category, News
from utils.base import NewsItemBase


#定义操作数据库的方法
# 获取新闻分类
async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 100):
    #查询新闻缓存分类
    categoryed_cache = await get_news_categories_cache()
    if categoryed_cache:
        return categoryed_cache

    query=select(Category).offset(skip).limit(limit)#分页查询
    result=await db.execute(query)
    categoryed = result.scalars().all()#orm对象

    #将查询结果写入缓存
    if categoryed:
        #将ORM对象转换为json格式
        categoryed_cache= jsonable_encoder(categoryed)
        await set_news_categories_cache(categoryed_cache)

    #返回结果
    return categoryed

#查询指定分类下的新闻
async def get_news_list(db: AsyncSession,category_id: int,page: int = 0, limit: int = 10):
    #查询指定分类下的新闻
    """
    获取新闻列表
    :param db: 数据库会话参数
    :param category_id: 分类ID
    :param page: 跳过的数量
    :param limit: 每页数量
    :return: 新闻列表
    """
    #offset: 跳过数量
    #limit: 限制数量
    #跳过的数量=（页码-1）*每页数量
    skip = (page - 1) * limit

    #查询新闻缓存
    news_list_cache = await get_news_list_cache(category_id, page, limit)#查询 json格式
    if news_list_cache:
        #return news_list_cache 直接返回也可
        return [News(**item) for item in news_list_cache]#将json格式转换为ORM对象

    query=select(News).where(News.category_id==category_id).offset(skip).limit(limit)#分页查询
    result=await db.execute(query)
    news_list= result.scalars().all()
    #写入缓存
    if news_list:
        news_list_cache = jsonable_encoder(news_list)#将ORM对象转换为json格式
        await set_news_list_cache(category_id, page, limit, news_list_cache)
        #orm 转成 Pydantic 再转为 字典
        #by_alias=False 不使用别名
        # news_data = [NewsItemBase(**item).model_dump(mode="json",by_alias=False) for item in news_list]
        # await set_news_list_cache(category_id, page, limit, news_data)

    return news_list

#获取新闻总数量
async def get_news_total(db: AsyncSession, category_id: int):
    query=select(func.count(News.id)).where(News.category_id==category_id)
    result=await db.execute(query)
    return result.scalar_one() #只能有一个结果，否则要报错

#获取新闻详情
async def get_news_detail(db: AsyncSession,new_id: int):
    query=select(News).where(News.id==new_id)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#判断新闻是否存在
async def news_view_update(db: AsyncSession, new_id: int):
    query=update(News).where(News.id==new_id).values(views=News.views+1)
    result=await db.execute(query)
    # await db.commit()

    #更新 → 检查数据库是否真的命中了数据→ 命中了返回True
    #result.rowcount: 受影响的行数
    return result.rowcount > 0

#返回推荐新闻
async def get_related_news(db: AsyncSession, new_id,category_id: int, limit: int = 5):
    query=select(News).where(
        News.category_id==category_id,
        News.id!=new_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result=await db.execute(query)
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in result.scalars().all()]







