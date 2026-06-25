#检查当前用户是否收藏
from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def is_new_favorite(
        db: AsyncSession,
        news_id: int,
        user_id: int,
):
    query =  select(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(query)

    # is not None：判断返回值是否不为None
    # 如果找到了收藏记录 → scalar_one_or_none()返回Favorite对象 → is not None返回Favorite对象 → is not None为True
    # 如果没有找到收藏记录 → scalar_one_or_none()返回None → is not None为False

    return result.scalar_one_or_none() is not None

async def add_new_favorite(
        db: AsyncSession,
        news_id: int,
        user_id: int,
):
    favorite=Favorite(news_id=news_id, user_id=user_id)

    db.add(favorite)

    # await db.commit()
    # await db.refresh(favorite)
    #返回最新的收藏记录

    try:
        await db.flush()  # 刷新以触发约束检查
    except IntegrityError:
        raise HTTPException(status_code=400, detail="已收藏过该新闻")

    return favorite

#取消收藏
async def remove_news_favorite(
        db: AsyncSession,
        news_id: int,
        user_id: int,
):

    query = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)

    try:
        await db.flush()  # 刷新以触发约束检查
    except IntegrityError:
        raise HTTPException(status_code=400, detail="该新闻未被收藏")

    #检查命中数量
    return result.rowcount > 0

#获取收藏列表
async def get_news_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int=1,
        page_size: int=10,
):
    #总量+收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    #获取收藏列表
    #select(查询主题模型类，字段别名).join(联合查询的模型类，连个查询的条件).where().order_by().offset().limit()
    offset = (page - 1) * page_size
    #返回收藏列表：[
    #   (新闻对象,收藏时间,收藏id)
    # ]
    query = (select(News, Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
             #join(联合查询的模型类，连个查询的条件)
             .join(Favorite,Favorite.news_id == News.id)
             #确定查询的字段
             .where(Favorite.user_id == user_id)
             #根据收藏时间排序
             .order_by(Favorite.created_at.desc())
             #分页查询
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

#清空收藏夹
async def clear_all_favorite(
        db: AsyncSession,
        user_id: int,
):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result=await db.execute(query)
    await db.commit()
    return result.rowcount or 0



