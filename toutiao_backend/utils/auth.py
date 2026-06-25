from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import create_db
from crud.users import get_user_by_token


async def get_current_user(
        authorization: str = Header(...,alias="Authorization"),
        db: AsyncSession = Depends(create_db)
):
    """
    根据Token查询用户，返回用户
    """
    # token=token.split(" ")[1]
    # token=authorization.replace("Bearer ","")
    # user = await get_user_by_token(db, token)
    #
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    #
    # return user

    # 兼容处理：如果没有 Bearer 前缀，直接使用整个字符串作为 token
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # 去掉 "Bearer " 前缀
    elif authorization.startswith("Bearer"):
        # 兼容 "Bearer" 后面没有空格的情况
        token = authorization[6:].lstrip()
    else:
        # 直接使用整个字符串作为 token（兼容前端未添加前缀的情况）
        token = authorization

    if not token:
        raise HTTPException(status_code=401, detail="缺少Token")

    user = await get_user_by_token(db, token)

    if not user:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    return user