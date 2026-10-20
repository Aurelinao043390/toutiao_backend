"""
配置ORM
一 安装ORM相关
    1 安装sqlalchemy核心
        pip install sqlalchemy
    2安装异步数据库驱动（根据数据库类型二选一）
        pip install pymysql 同步
        pip install aiomysql 异步
    FastAPI 本身是异步框架，为了充分发挥其性能优势，建议使用 aiomysql + SQLAlchemy 异步模式


二 新建模型表
    1 创建异步引擎、异步会话工厂、依赖项
    2 定义模型基类和模型类
    3 建表
三 操作数据库
    1 路由处理函数注入数据库会话的依赖项Denpends
    2 增删改查
        db.excute()
        select()
        add()
        delete()
        update则是重新赋值

项目开发中 ，这里将引擎、会话工厂和基类集中管理，封装在1个文件里，方便调用
"""

from dotenv import load_dotenv
import os

load_dotenv(override=True)
ASYNC_DB_URL=os.getenv("ASYNC_DB_URL")


# 二 新建模型表
#     1.1 创建异步引擎
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.ext.asyncio.session import AsyncSession


async_engine=create_async_engine(
    ASYNC_DB_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=300

)



#     1.2 异步会话工厂

AsyncSessionLocal=async_sessionmaker(
    bind=async_engine,#指定异步的数据库引擎
    expire_on_commit=False,#提交会话后，设置会话session不会过期
    class_=AsyncSession#制定会话类别是异步的

)

#     1.3 AsyncSession 封装成依赖项

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回数据库会话给路由处理函数
            # yield 和普通的 return 有点类似，都是向外部提供一个数据（在这里是session数据库会话）。 但return 会直接结束函数并销毁内部状态，
            # 而yield 则是 “暂停” 函数。它把 session给出去供外部使用，并等待外部使用完毕后，函数会继续往下执行。
            await session.commit() #提交事务
        except Exception as e:
            await session.rollback()#异常回滚
            raise e
        finally:
            await session.close()#关闭事务
# 2 创建关系依赖
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

#已经使用sql文件创建了所有的基础表，不再需要在orm中去创建了