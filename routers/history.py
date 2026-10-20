from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel,Field
from sqlalchemy.ext.asyncio import AsyncSession

from crud import users,history,news
from config.db_conf import get_db
from schemas.users import UserRequestModel, UserAuthResponse, UserInfoResponse, UserInfoUpdate, PasswordUpdate
from starlette import status
from utils.auth import get_current_user
from utils.response import success_response
from schemas.history import HistoryRequestResponse,AddHistoryRequestResponse,HistoryListRequestResponse
# 创建api_router的实例
# prefix 路由前缀
# tags 路由的标签，用于分组显示
api_router = APIRouter(prefix="/api/history", tags=["history"])

#1 用户注册 请求方法POST，参数Pydantic类型。需要先检查用户名是否存在重复的，如果有重复则抛出异常，没有重复则创建对应用户名，保存用户名，同时对密码进行加密保存，然后返回访问令牌
@api_router.post("/add")
async def add_history(
        news_data: AddHistoryRequestResponse,
        current_user: UserInfoResponse = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
    add_history_result=await history.add_history(current_user.id,news_data.news_id,db)
    if not add_history_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="添加浏览历史记录失败")
    return success_response(message="添加成功",data=add_history_result)
#2. 获取浏览历史列表 请求方法GET，参数Pydantic类型。需要返回用户浏览历史列表
@api_router.get("/list")
async def get_history_list(user:UserInfoResponse=Depends(get_current_user),page:int=1,page_size:int =10,db:AsyncSession=Depends(get_db)):
    """
    查询用户收藏的新闻列表
    """

    history_list,total = await history.get_history_news_list(user.id,page,page_size,db)
    has_more= total > (page * page_size)
    history_news_list=[
        {
            **news_row.__dict__,
            "view_time": view_time
        }
        for news_row, view_time in history_list
    ]
    data=HistoryListRequestResponse(list=history_news_list, total=total, has_more=has_more)

    return success_response(message="success",data=data)
@api_router.delete("/delete/{history_id}")
async def delete_history(history_id:int=Path(...,description="历史记录ID"),current_user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    删除用户的1个浏览历史记录
    """
    delete_history_result=await history.delete_history(current_user.id,history_id,db)
    if not delete_history_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除浏览历史记录失败")
    return success_response(message="删除成功")
@api_router.delete("/clear")
async def delete_all_history(current_user:UserInfoResponse=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    """
    删除用户所有浏览历史记录
    """
    delete_all_history_result=await history.delete_all_history(current_user.id,db)
    if not delete_all_history_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除所有浏览历史记录失败")
    return success_response(message="删除成功",data=None)
