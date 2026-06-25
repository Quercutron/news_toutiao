from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str]=None
    image: Optional[str]=None
    author: Optional[str]=None
    category_id: int = Field(alias="categoryId")
    views:int
    publish_time: Optional[datetime]=Field(None,alias="publishTime")

    model_config = ConfigDict(
        # 配置模型类，允许从属性中获取数据，并按名称填充数据
        from_attributes=True,
        populate_by_name=True,
    )