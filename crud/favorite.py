import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio  import AsyncSession
from sqlalchemy import Select, Delete, join,func


from config.db_conf import get_db
from models.favorite import Favorite
from models.news import News
from starlette import status

from models.users import User
from schemas.users import UserInfoResponse
from utils.auth import get_current_user


#检查收藏状态，当前用户是否收藏了这1条新闻
async def is_news_favorite(user_id:int,news_id:int,db:AsyncSession=Depends(get_db)):
    query= Select(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(query)
    favorite_result=result.scalar_one_or_none()
    if not favorite_result:
        return False
    else:
        return True

#添加用户收藏的新闻
async def add_favorite(user_id:int,news_id:int,db:AsyncSession=Depends(get_db)):
    #检查是否已经被当前用户收藏，如果没有，则执行新增，否则报错不执行
    favorite_result=await is_news_favorite(user_id,news_id,db)
    if favorite_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="数据库错误，该新闻已被当前用户收藏")
    else:
        favorite=Favorite(user_id=user_id,news_id=news_id)
        db.add(favorite)
        await db.commit()
        # 刷新一下，确保拿到是最新数据
        await db.refresh(favorite)
        return favorite
#取消用户收藏的新闻
async def remove_favorite(user_id:int,news_id:int,db:AsyncSession=Depends(get_db)):
    query = Delete(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(query)
    await db.commit()
    # if result.rowcount==0:
    #     return False
    # else:
    #     return True
    return result.rowcount>0
#获取用户收藏的新闻列表
async def get_favorite_list(user_id:int,page:int=1,page_size:int=10,db:AsyncSession=Depends(get_db)):

    #查询到的收藏的新闻的总量
    count_query=Select(func.count(News.id)).where(Favorite.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one()
    #获取收藏列表
    offset=(page-1)*page_size
    query = (
        Select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
            .join(Favorite ,News.id==Favorite.news_id)
            .where(Favorite.user_id==user_id)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(page_size)
             )
    result=await db.execute(query)
    favorite_list=result.all()
    return favorite_list,total
#清空用户收藏的新闻
async def remove_favorite_list(user_id: int,db:AsyncSession=Depends(get_db)):
    query = Delete(Favorite).where(Favorite.user_id==user_id)
    result=await db.execute(query)
    await db.commit()
    rows_count=result.rowcount
    return rows_count