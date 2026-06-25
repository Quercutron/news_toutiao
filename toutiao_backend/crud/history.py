from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


#定义浏览新闻历史方法
async def add_history(
        db: AsyncSession,
        news_id: int,
        user_id: int
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    # 获取历史记录结果为：History对象或None
    existing_history = result.scalar_one_or_none()

    if existing_history:
        existing_history.view_time = datetime.now()
        # await db.commit()
        await db.flush()  # 刷新以触发约束检查
        # 刷新existing_history对象
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(news_id=news_id, user_id=user_id)
        db.add(history)
        # await db.commit()
        await db.flush()  # 刷新以触发约束检查
        await db.refresh(history)
        return history

#获取新闻历史列表
async def get_news_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
):
    #总量+收藏的新闻列表
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    #获取收藏列表
    #select(查询主题模型类，字段别名).join(联合查询的模型类，连个查询的条件).where().order_by().offset().limit()
    offset = (page - 1) * page_size
    #返回收藏列表：[
    #   (新闻对象,历史记录id,浏览时间)
    # ]
    query = (select(News,History.view_time)
             #join(联合查询的模型类，连个查询的条件)
             .join(History,History.news_id == News.id)
             #确定查询的字段
             .where(History.user_id == user_id)
             #根据收藏时间排序
             .order_by(History.view_time.desc())
             #分页查询
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

#删除单条浏览记录
async def delete_one_history(
        history_id: int,
        user_id: int,
        db: AsyncSession,
):
    query=delete(History).where(History.id == history_id)
    result=await db.execute(query)
    await db.flush()

    return result.rowcount>0

#清空浏览历史
async def clear_all_history(
        db: AsyncSession,
        user_id: int
):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0
