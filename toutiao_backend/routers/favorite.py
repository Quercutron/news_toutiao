from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import create_db
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite


router = APIRouter(prefix="/api/favorite", tags=["favorite"])


#检查用户是否已收藏新闻
@router.get("/check")
async def check_favorite(
        news_id: int=Query(...,alias="newsId"),
        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db)
):
    is_favorited = await favorite.is_new_favorite(db, news_id, user.id)

    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorited))

#添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        db: AsyncSession = Depends(create_db),
        user:User=Depends(get_current_user),
):
    new_favorite=await favorite.add_new_favorite(db, data.news_id, user.id)
    return success_response(message="添加收藏成功",data=new_favorite)

#取消收藏
@router.delete("/remove")
async def remove_favorite(
        news_id: int=Query(...,alias="newsId"),
        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db)
):
    result=await favorite.remove_news_favorite(db, news_id, user.id)
    if not result:
        raise HTTPException(status_code=400, detail="该新闻未被收藏")
    return success_response(message="取消收藏成功")

#获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, alias="page", ge=1),
        page_size: int = Query(10, alias="pageSize"),
        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db)
):

    rows,total=await favorite.get_news_favorite_list(db, user.id, page, page_size)
    #将查询结果转换为字典列表，包含新闻信息和收藏时间、收藏id
    favorite_list=[{
        **news.__dict__,
        "favoriteTime": favorite_time,
        "favoriteId": favorite_id
    } for news,favorite_time,favorite_id in rows]

    #是否还有更多
    has_more = total > page * page_size

    data=FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)

    return success_response(message="获取收藏列表成功", data=data)

#清空收藏列表
@router.delete("/clear")
async def clear_favorite_list(
        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db)
):
    result=await favorite.clear_all_favorite(db, user.id)
    return success_response(message=f"清空{result}条收藏新闻！")

