import datetime


from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio  import AsyncSession
from sqlalchemy import Select, Delete, join, Update, func
from sqlalchemy.sql.functions import user

from config.db_conf import get_db
from models.history import History
from models.news import News
from starlette import status

from models.users import User
from schemas.users import UserInfoResponse
from utils.auth import get_current_user


# #检查浏览历史表，当前用户是否已经浏览过了这1条新闻
async def is_view_news(user_id:int,news_id:int,db:AsyncSession=Depends(get_db)):
    query= Select(History).where(History.user_id==user_id,History.news_id==news_id)
    result=await db.execute(query)
    check_result=result.scalar_one_or_none()
    if not check_result:
        return False
    else:
        return True

#添加用户浏览的新闻历史
async def add_history(user_id:int,news_id:int,db:AsyncSession=Depends(get_db)):
        view_result= await is_view_news(user_id,news_id,db)
        if view_result: #如果用户已经浏览过这条新闻，则返回true
            query=Update(History).where(History.user_id==user_id,History.news_id==news_id).values(view_time=datetime.datetime.now())
            await db.execute(query)
            await db.commit()
            query=Select(History).where(History.user_id==user_id,History.news_id==news_id)
            result=await db.execute(query)
            history=result.scalar_one()
            await db.refresh(history)
            return history
        else:
            history=History(user_id=user_id,news_id=news_id)
            db.add(history)
            await db.commit()
            # 刷新一下，确保拿到是最新数据
            await db.refresh(history)
            return history
#删除用户浏览的新闻历史
async def delete_history(user_id:int,history_id:int,db:AsyncSession=Depends(get_db)):
    query = Delete(History).where(History.user_id==user_id,History.id==history_id)
    result=await db.execute(query)
    await db.commit()
    # if result.rowcount==0:
    #     return False
    # else:
    #     return True
    return result.rowcount>0
# #获取用户浏览的历史新闻列表
async def get_history_news_list(user_id:int,page:int=1,page_size:int=10,db:AsyncSession=Depends(get_db)):

    #查询到的浏览历史的新闻的总量
    count_query = Select(func.count(History.id)).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    #获取浏览历史列表
    offset=(page-1)*page_size
    query = (
        Select(News, History.view_time.label("view_time"))
        .join(History, News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    favorite_list = result.all()
    return favorite_list, total
# #清空用户收藏的新闻
async def delete_all_history(user_id: int,db:AsyncSession=Depends(get_db)):
    query = Delete(History).where(History.user_id==user_id)
    result=await db.execute(query)
    await db.commit()
    rows_count=result.rowcount
    return rows_count