from sqlalchemy import select,func,update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News

#新闻模块的增删改查
#获取所有新闻分类
async def get_categories(db:AsyncSession,skip=0,limit:int=100):
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()
#获取指定分类相关的新闻
async def get_news_list(db:AsyncSession,category_id=0,skip=0,limit:int=10):
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()
#获取指定分类相关的新闻的总数量
async def get_news_count(db:AsyncSession,category_id=0,skip=0,limit:int=10):

    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result=await db.execute(stmt)
    total= result.scalar_one()
    return total
#获取指定新闻id的新闻详情
async def get_news_detail(db:AsyncSession,news_id=0):

    stmt=select(News).where(News.id==news_id)
    result=await db.execute(stmt)
    news_detail=result.scalar_one_or_none()

    return news_detail
#指定新闻的浏览次数加1
async def increase_views(db:AsyncSession,news_id=0,):
    stmt=update(News).where(News.id==news_id).values(views=News.views+1)
    result=await db.execute(stmt)
    await db.commit()
    return  result.rowcount>0
    # for attr in sorted(dir(result)):
    #     if not attr.startswith('_'):
    #         try:
    #             value = getattr(result, attr)
    #             # 跳过方法和类本身，只关注数据属性
    #             if not callable(value):
    #                 print(f"{attr:30s} = {value!r}")
    #         except Exception as e:
    #             print(f"{attr:30s} = <ERROR: {e}>")
    # 使用上面代码的输出update执行后得到result的内容如下
    # closed = False
    # connection = < sqlalchemy.engine.base.Connection    object    at    0x0000012A81783A80 >
    # context = < sqlalchemy.dialects.mysql.mysqldb.MySQLExecutionContext_mysqldb    object    at    0x0000012A8186AF10 >
    # cursor = None
    # cursor_strategy = < sqlalchemy.engine.cursor.NoCursorDMLFetchStrategy    object    at    0x0000012AFFB85460 >
    # dialect = < sqlalchemy.dialects.mysql.aiomysql.MySQLDialect_aiomysql    object    at    0x0000012A814EDA90 >
    # inserted_primary_key = < ERROR: Statement is not an    insert()    expression    construct. >
    # inserted_primary_key_rows = < ERROR: Statement is not an    insert()    expression    construct. >
    # is_insert = False
    # lastrowid = 0
    # returned_defaults = None
    # returned_defaults_rows = None
    # returns_rows = False
    # rowcount = 1
    # t = < sqlalchemy.engine.cursor.CursorResult    object    at    0x0000012A818C0510 >
#获取同类相关新闻的
async def get_related_news(db:AsyncSession,news_id=0,category_id=0,limit:int=5):
    #orderby 排序 按照浏览量和发布时间 降序排序
    stmt=(
        select(News)
        .where(News.id!=news_id  ,News.category_id==category_id)
        .order_by(News.views.desc(),News.publish_time.desc())
        .limit(limit)
    )
    result=await db.execute(stmt)
    # related_news获取到的是一个News对象的列表，每个新闻包含了所有的属性，但是没有必要返回给前端所有数据，因此使用列表推导式构建新的news列表
    related_news=result.scalars().all()
    return [{
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views,
    }for news in related_news
    ]
