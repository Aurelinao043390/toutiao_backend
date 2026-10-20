from datetime import datetime
from config.db_conf import async_engine
from sqlalchemy import DateTime, Integer, String, Text, Index, Column,ForeignKey,ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    """Base class for all mapped classes"""
    pass

#新闻收藏表的基类
class Favorite(Base):
    __tablename__="favorite"
    #为了工程可维护性，ORM的索引内容保持与数据库同步。否则下次迁移时会导致数据库性能差异
    #创建对应的索引
    __table_args__ = (

        Index("user_news_unique",
              Column("user_id").asc(),Column("news_id").asc()
              ),
        Index("fk_favorite_user_idx",
              Column("user_id").asc(),
              ),
        Index("fk_favorite_news_idx",
             Column("news_id").asc()
               )
    )
    # 格式：(本地字段, 远程表.远程字段, 约束名称)
    ForeignKeyConstraint(
        ["news_id"],
        ["news_app.news.id"],  # 以防在多租户系统或者跨数据库关联，明确指定被引用的模式是news_app
        name="fk_favorite_news"

    ),
    # 格式：(本地字段, 远程表.远程字段, 约束名称)
    ForeignKeyConstraint(
        ["user_id"],
        ["news_app.user.id"],  # 以防在多租户系统或者跨数据库关联，明确指定被引用的模式是news_app
        name="fk_favorite_user"

    ),
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,nullable=True,comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer,  nullable=True, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer,  nullable=True, comment="新闻ID")
    created_at:Mapped[datetime]=mapped_column(DateTime,nullable=True,default=datetime.now,comment="创建时间")


