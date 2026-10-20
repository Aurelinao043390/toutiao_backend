from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel,Field
from sqlalchemy.ext.asyncio import AsyncSession

from crud import users,favorite
from config.db_conf import get_db
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from schemas.users import UserRequestModel, UserAuthResponse, UserInfoResponse, UserInfoUpdate, PasswordUpdate
from starlette import status
from utils.auth import get_current_user
from utils.response import success_response

# 创建api_router的实例
# prefix 路由前缀
# tags 路由的标签，用于分组显示
api_router = APIRouter(prefix="/api/favorite", tags=["favorite"])
@api_router.get("/check")
async def check_favorite(news_id:int=Query(...,alias="newsId"),user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    检查新闻是否被用户收藏
    """
    is_favorite=await favorite.is_news_favorite(user.id,news_id,db)
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorite))

@api_router.post("/add")
async def add_favorite(news_data:FavoriteAddRequest,user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    添加用户收藏的新闻
    """
    add_favorite_result=await favorite.add_favorite(user.id,news_data.news_id,db)
    return success_response(message="添加收藏状态成功",data=add_favorite_result)
@api_router.delete("/remove")
async def remove_favorite(news_id:int=Query(...,alias="newsId"),user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    取消用户收藏的新闻
    """
    remove_favorite_result=await favorite.remove_favorite(user.id,news_id,db)
    if  not remove_favorite_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="取消收藏失败")
    return success_response(message="取消收藏状态成功")

@api_router.get("/list")
async def get_favorite_list(user:UserInfoResponse=Depends(get_current_user),page:int=1,page_size:int =10,db:AsyncSession=Depends(get_db)):
    """
    查询用户收藏的新闻列表
    """

    favorite_list,total = await favorite.get_favorite_list(user.id,page,page_size,db)
    has_more= total > (page * page_size)
    favorite_news_list=[
        {
            **favorite_news.__dict__,
            "favorite_time":favorite_time,
            "favorite_id":favorite_id
        }
        for favorite_news,favorite_time,favorite_id in favorite_list
    ]
    data=FavoriteListResponse(list=favorite_news_list, total=total,  has_more=has_more)

    return success_response(message="获取收藏列表成功",data=data)
@api_router.delete("/clear")
async def clear_favorite_list(user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    清空用户收藏的新闻列表
    """
    clear_count=await favorite.remove_favorite_list(user.id,db)
    return success_response(message=f"成功删除{clear_count}条收藏记录",data=None)
