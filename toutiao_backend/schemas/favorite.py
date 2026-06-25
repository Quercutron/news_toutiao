from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from utils.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool=Field(..., alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

#规划两个类，一个是新闻模型类，一个收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    category_id: int = Field(alias="categoryId")
    views: int = Field(alias="views")
    favorite_time: datetime = Field(alias="favoriteTime")


    model_config = ConfigDict(
        # 配置模型类，允许从属性中获取数据，并按名称填充数据
        from_attributes=True,
        populate_by_name=True,
    )



#定义响应收藏列表接口的模型类
class FavoriteListResponse(BaseModel):
    list: list [FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        # 配置模型类，允许从属性中获取数据，并按名称填充数据
        from_attributes=True,
        populate_by_name=True,
    )