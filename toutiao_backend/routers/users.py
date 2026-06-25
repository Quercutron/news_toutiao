from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateResponse, UserPasswordResponse
from crud import users
from config.db_config import create_db
from utils.auth import get_current_user
from utils.response import success_response

#创建APIRouter实例，模块化路由
#prefix: 路由前缀（API接口规范文档）
#tags: 分组 标签
router = APIRouter(prefix="/api/user", tags=["user"])

#注册用户
@router.post("/register")
async def register(user_data: UserRequest,db: AsyncSession = Depends(create_db)):
    # 注册逻辑:验证用户是否存在 -> 创建用户 →生成 Token →响应结果
    existing_user=await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户已存在")

    user = await users.create_user(db, user_data)

    token = await users.create_token(db, user)


    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         },
    #     }
    # }
    response_data=UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)

#用户登录
@router.post("/login")
async def login(
        user_data: UserRequest,
        db: AsyncSession = Depends(create_db)
):
    #检查用户是否存在，生成访令牌，响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        #抛出具体的业务错误
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = await users.create_token(db, user)

    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)

#查Token查用户，封装crud，功能整合成一个函数，路由导入使用
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

#修改用户信息
@router.put("/update")
async def update_user_info(
        user_data: UserUpdateResponse,
        db: AsyncSession = Depends(create_db),
        user: User = Depends(get_current_user)
):
    update_user=await users.update_user(db, user.username, user_data)
    #model_dump:将pydantic对象数据转换为字典
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(update_user))

#修改用户密码
@router.put("/update/password")
async def update_user_password(
        password_data: UserPasswordResponse,
        db: AsyncSession = Depends(create_db),
        user: User = Depends(get_current_user)
):
    result=await users.update_user_password(db, user, password_data.old_password, password_data.new_password)
    if not result:
        raise HTTPException(status_code=400, detail="旧密码错误")
    return success_response(message="更新用户密码成功")

