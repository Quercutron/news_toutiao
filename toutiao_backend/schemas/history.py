from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from utils.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int=Field(...,alias="newsId",description="新闻ID")
    """
    discriminator 的用途错误
    discriminator 是用于**联合类型（Union）**的区分标识，不是字段描述
    它告诉 Pydantic 如何区分不同的类型变体
    只能用于 Union 类型，不能用于 int、str 等基础类型
    """


#规划两个类，一个是新闻模型类，一个历史的模型类
class HistoryNewsItemResponse(NewsItemBase):
    views: int = Field(alias="views")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        # 配置模型类，允许从属性中获取数据，并按名称填充数据
        from_attributes=True,
        populate_by_name=True,
    )

#定义响应收藏列表接口的模型类
class HistoryListResponse(BaseModel):
    list: list [HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        # 配置模型类，允许从属性中获取数据，并按名称填充数据
        from_attributes=True,
        populate_by_name=True,
    )
