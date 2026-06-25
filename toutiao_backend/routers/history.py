from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import create_db
from crud import history
from crud.history import clear_all_history
from models.users import User
from schemas.favorite import FavoriteListResponse
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db),
):
    result = await history.add_history(db, data.news_id, user.id)
    #data: 返回历史记录数据
    return success_response(message="浏览历史添加成功", data=result)

@router.get("/list")
async def get_history_list(
        page: int = 1,
        page_size: int = Query(10,ge=1,le=100, alias="pageSize"),
        user: User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db),
):
    rows,total=await history.get_news_history_list(db, user.id, page, page_size)
    #将查询结果转换为字典列表，包含新闻信息和浏览时间
    history_list=[{
        **news.__dict__,
        "viewTime": view_time
    } for news,view_time in rows]

    #是否还有更多
    has_more = total > page * page_size

    data=HistoryListResponse(list=history_list, total=total, hasMore=has_more)

    return success_response(message="获取历史记录成功", data=data)

@router.delete("/delete/{history_id}")
async def delete_history(
        history_id: int,
        user: User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db),
):
    await history.delete_one_history(history_id, user.id, db)
    return success_response(message="浏览历史删除成功")

@router.delete("/clear")
async def clear_history(
        user: User=Depends(get_current_user),
        db: AsyncSession = Depends(create_db),
):
    result=await clear_all_history(db, user.id)
    return success_response(message=f"清空了{result}条浏览历史")