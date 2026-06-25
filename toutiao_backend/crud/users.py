import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateResponse
from utils import security


#根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    query =select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    #进行加密处理
    hashed_password = security.get_password_hash(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) # 从数据库中读回最新的数据
    return user

#创建Token
async def create_token(db: AsyncSession, user: User):
    #生成Token+设置过期时间 → 查询数据库当前用户是否有Token → 没有：创建Token，有：更新Token
    token=str(uuid.uuid4())
    #设置过期时间
    expires_at=datetime.now()+timedelta(days=7)
    #判断当前用户是否有Token
    query=select(UserToken).where(UserToken.user_id == user.id)
    result = await db.execute(query)
    user_token=result.scalar_one_or_none()

    #没有Token：创建Token
    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
        await db.commit()
    else:
        user_token = UserToken(user_id=user.id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

#用户登录验证
async def authenticate_user(db: AsyncSession, username: str, password: str):
    #查询用户
    user = await get_user_by_username(db, username)
    if not user:
        return None
    #验证密码
    if not security.verify_password(password, user.password):
        return None

    return user

#根据Token查询用户：验证Token，查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query=select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if not user_token or user_token.expires_at < datetime.now(): # Token过期
        return None

    query=select(User).where(User.id == user_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#更新用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateResponse):
    """
    根据用户名更新用户信息
    """
    #model_dump:将pydantic对象数据转换为字典
    update_query=update(User).where(User.username == username).values(**user_data.model_dump(
        #检查是否有设置
        exclude_unset=True,
        #检查是否为空
        exclude_none=True
    ))
    result=await db.execute(update_query)
    await db.commit()

    #rowcount: 受影响的行数
    if result.rowcount==0:
        raise HTTPException(status_code=404, detail="User not found")

    #获取更新后的用户
    updated_user = await get_user_by_username(db, username)
    return updated_user

#修改用户密码
async def update_user_password(db: AsyncSession, user: User, old_password: str, new_password: str):

    #验证旧密码与数据库密码是否匹配,若不匹配则返回False
    if not security.verify_password(old_password, user.password):
        raise False

    hashed_password = security.get_password_hash(new_password)

    user.password = hashed_password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True