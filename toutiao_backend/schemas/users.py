from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):

    username: str = Field(..., max_length=50, description="用户名")
    password: str = Field(..., min_length=3, max_length=72, description="密码（最长72字节）")

#基础类
class UserInfoBase(BaseModel):
     """
     用户信息基础数据模型
     """
     nickname: Optional[str] = Field(None, max_length=50, description="昵称")
     avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
     gender: Optional[str] = Field(None, max_length=10, description="性别")
     bio: Optional[str] = Field(None, max_length=500, description="个人简介")


#user_info对应的类：基础类 + info类（id，用户名）
class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    #模型配置类
    model_config = ConfigDict(
        from_attributes=True#允许从ORM对象属性中中获取数据
    )


#data数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse=Field(..., alias="user_info")

    #模型配置类
    model_config = ConfigDict(
        populate_by_name=True,#alias字段名兼容
        from_attributes=True#允许从ORM对象属性中中获取数据
    )

#修改用户信息的响应格式
class UserUpdateResponse(BaseModel):
    """
    用户信息更新响应数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str]=Field(None, max_length=255, description="手机号")

#修改用户密码响应格式
class UserPasswordResponse(BaseModel):
    """
    用户密码更新响应数据模型
    """
    old_password: str=Field(..., alias="oldpassword", description="旧密码（最长72字节）")
    new_password: str=Field(..., alias="newpassword", min_length=6,description="新密码（最长72字节）")

