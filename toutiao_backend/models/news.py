from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, func, Index, ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase

#mapped：设置属性类型
#mapped_column：映射字段

#定义基础模型类，数据库字段映射
class Base(DeclarativeBase):
    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )


class Category(Base):
    __tablename__ = 'news_category'

    #autoincrement：自增
    #unique：唯一
    #nullable：是否为空
    #comment：字段注释
    #default：默认值
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="分类ID")
    name:Mapped[str]=mapped_column(String(50),nullable=False,unique=True,comment="分类名称")
    sort_order:Mapped[int]=mapped_column(Integer,default=0,comment="自增")

    def __repr__(self):
        #类似Python的__str__方法
        return f"<Category (id={self.id}, name={self.name}, sort_order={self.sort_order})>"


class News (Base):
    __tablename__ = "news"

    #创建索引:提升查询速度
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),#高频查询场景
        Index('idx_publish_time', 'publish_time')#按发布时间排序
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped [str] = mapped_column(String(255), nullable=False, comment="标题")
    description: Mapped [Optional[str]] = mapped_column(String(500), comment="描述")
    content: Mapped [str] = mapped_column(String(255), nullable=False, comment="内容")
    image: Mapped [Optional[str]] = mapped_column(String(255), comment="图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览次数")
    publish_time: Mapped [datetime] = mapped_column(DateTime, default=func.now(), comment="发布时间")

    def _repr_(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"

