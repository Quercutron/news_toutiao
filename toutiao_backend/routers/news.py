from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import news, news_cache

from config.db_config import create_db

#创建APIRouter实例，模块化路由
#prefix: 路由前缀（API接口规范文档）
#tags: 分组 标签
router = APIRouter(prefix="/api/news", tags=["news"])

#获取新闻分类列表
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(create_db)):
    """
    获取新闻分类列表
    :param skip: 跳过数量
    :param limit: 限制数量
    :param db: 数据库会话
    :return: 新闻分类列表
    """
    #先获取数据库里面的新闻分类数据 ➡先定义模型类 ➡封装查询数据的方法
    #调用crud层的get_categories方法获取数据,定义依赖项db
    categories = await news_cache.get_categories(db, skip, limit)

    return {
        "code": 200,
        "message": "Success",
        "data": categories
    }

@router.get("/list")
async def get_news(
        category_id: int = Query(...,alias="categoryId",),
        page: int = 1,
        page_size: int = Query(10,le=100,alias="pageSize"),
        db: AsyncSession = Depends(create_db)
):
    """
    获取新闻列表
    :param category_id: 分类ID
    :param page: 页码
    :param page_size: 每页数量
    :param db: 数据库会话
    :return: 新闻列表
    """
    #思路：处理分页规则 → 查询新闻列表 → 计算总条数 → 判断是否有更多数据
    offset = (page - 1) * page_size#跳过数量
    news_list = await news_cache.get_news_list(db, category_id, page, page_size)
    total = await news_cache.get_news_total(db, category_id)
    #判断是否还有更多数据:跳过数量+当前数量<总数量
    has_more =( offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "Success",
        "data": {
                "list": news_list,
                "total": total,
                "hasMore": has_more,#是否还有更多
        }
    }

@router.get("/detail")
async def get_news_detail(
        new_id: int=Query(...,alias="id",),
        db: AsyncSession = Depends(create_db)
):
    #获取新闻详情
    news_detail = await news.get_news_detail(db, new_id)
    if not news_detail :
        raise HTTPException(status_code=404, detail="News not found")

    result=await news.news_view_update(db, news_detail.id)
    if not result:
        raise HTTPException(status_code=404, detail="News not found")

    related_news=await news.get_related_news(db,news_detail.id,news_detail.category_id)

    return {
        "code": 200,
        "message": "Success",
        "data":{
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }


