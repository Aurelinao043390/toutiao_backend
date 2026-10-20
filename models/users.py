from datetime import datetime

from config.db_conf import async_engine
from sqlalchemy import DateTime, Integer, String, Text, Index, Column,ForeignKey,ForeignKeyConstraint,Enum
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    """Base class for all mapped classes"""
    pass
#用户列表的基类
class User(Base):
    __tablename__="user"
    #为了工程可维护性，ORM的索引内容保持与数据库同步。否则下次迁移时会导致数据库性能差异
    #创建对应的索引
    __table_args__ = (

        Index("username_UNIQUE",
              Column("username").asc()#声明用户名的升序索引
              ),
        Index("phone_UNIQUE",
              Column("phone").desc()#声明电话号码的降序索引
        )
    )
    # 格式：(本地字段, 远程表.远程字段, 约束名称) 该表没有外键

    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,nullable=False,comment="用户ID")
    username:Mapped[str]=mapped_column(String(50),nullable=False,comment="用户名称")
    password:Mapped[str]=mapped_column(String(255),nullable=False,comment="用户密码，加密存储")
    nickname:Mapped[str]=mapped_column(String(50),nullable=True,comment="用户昵称")
    avatar:Mapped[str]=mapped_column(String(255),nullable=False,comment="头像URL")
    gender:Mapped[Enum]=mapped_column(Enum("Male", "Female"),nullable=False,comment="性别")
    bio:Mapped[str]=mapped_column(String(500),nullable=True,comment="个人简介")
    phone:Mapped[str]=mapped_column(String(20),nullable=True,comment="手机号")
    created_at:Mapped[datetime]=mapped_column(DateTime,nullable=False,default=datetime.now,comment="创建时间")
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=False,default=datetime.now,onupdate=datetime.now,comment="更新时间")

class UserToken(Base):
    __tablename__ = "user_token"
    # 为了工程可维护性，ORM的索引内容保持与数据库同步。否则下次迁移时会导致数据库性能差异
    # 创建对应的索引
    __table_args__ = (

        Index("token_UNIQUE",
              Column("token").asc()
              ),
        Index("fk_user_token_user_idx",
              Column("user_id").asc()
              )
    )
    # 格式：(本地字段, 远程表.远程字段, 约束名称) 该表没有外键
    ForeignKeyConstraint(
        ["user_id"],
        ["news_app.user.id"],  # 以防在多租户系统或者跨数据库关联，明确指定被引用的模式是news_app
        name="fk_user_token_user"
    ),
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")#不在这里进行创建时间+7天的运算
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now,   comment="创建时间")