from datetime import datetime
from config.db_conf import async_engine
from sqlalchemy import DateTime, Integer, String, Text, Index, Column,ForeignKey,ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    """Base class for all mapped classes"""
    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )
#新闻分类表的基类
class Category(Base):
    __tablename__="news_category"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="分类ID")
    name:Mapped[str]=mapped_column(String(50),nullable=False,comment="新闻分类")
    sort_order:Mapped[int]=mapped_column(Integer,default=0,nullable=False,comment="排序码")

    def __repr__(self):
        return f"<Category(id={self.id},name={self.name},sort_order={self.sort_order})>"

    # 根据模型自动建表（表不存在才创建，由于已经手动创建了数据库表，这里跳过不执行）
    # Base.metadata.create_all(async_engine)

#新闻详情列表的基类
class News(Base):
    __tablename__="news"
    #为了工程可维护性，ORM的索引内容保持与数据库同步。否则下次迁移时会导致数据库性能差异
    #创建对应的索引
    __table_args__ = (

        Index("fk_news_category_idx",
              Column("category_id").asc()#声明分类ID的升序索引
              ),
        Index("idx_publish_time",
              Column("publish_time").desc()#声明发布时间的降序索引
        )
    )
    # 格式：(本地字段, 远程表.远程字段, 约束名称)
    ForeignKeyConstraint(
        ["category_id"],
        ["news_app.news_category.id"],  # 以防在多租户系统或者跨数据库关联，明确指定被引用的模式是news_app
        name="fk_news_category"
    ),
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,nullable=False,comment="新闻ID")
    title:Mapped[str]=mapped_column(String(255),nullable=True,comment="新闻标题")
    description:Mapped[str]=mapped_column(String(500),nullable=False,comment="新闻简介")
    content:Mapped[str]=mapped_column(Text(),nullable=True,comment="新闻内容")
    image:Mapped[str]=mapped_column(String(255),nullable=False,comment="封面图片URL")
    author:Mapped[str]=mapped_column(String(50),nullable=False,comment="作者")
    category_id:Mapped[int]=mapped_column(Integer,nullable=True,comment="分类ID")
    views:Mapped[int]=mapped_column(Integer,nullable=True,comment="浏览量")
    publish_time:Mapped[datetime]=mapped_column(DateTime,nullable=True,comment="发布时间")
    created_at:Mapped[datetime]=mapped_column(DateTime,nullable=False,default=datetime.now,comment="创建时间")
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=False,default=datetime.now,onupdate=datetime.now,comment="更新时间")
    #打印关键字段的函数
    def __repr__(self):
        return f"<News(id={self.id},title={self.title},category_id={self.category_id},created_at={self.created_at}>"
