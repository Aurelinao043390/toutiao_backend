from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.ext.asyncio import AsyncSession

from crud import users
from config.db_conf import get_db
from schemas.users import UserRequestModel, UserAuthResponse, UserInfoResponse, UserInfoUpdate, PasswordUpdate
from starlette import status
from utils.auth import get_current_user
from utils.response import success_response

# 创建api_router的实例
# prefix 路由前缀
# tags 路由的标签，用于分组显示
api_router = APIRouter(prefix="/api/user", tags=["users"])

#1 用户注册 请求方法POST，参数Pydantic类型。需要先检查用户名是否存在重复的，如果有重复则抛出异常，没有重复则创建对应用户名，保存用户名，同时对密码进行加密保存，然后返回访问令牌
@api_router.post("/register")
async def register(user_data:UserRequestModel,db:AsyncSession=Depends(get_db)):
    existed_user=await users.get_user_by_username(db,user_data.username)
    if existed_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user=await users.create_user(db, user_data)
    user_token=await users.create_token(db, user.id)
    response_data=UserAuthResponse(token=user_token,userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)



#2 用户登录
@api_router.post("/login")
async def login( user_data:UserRequestModel,db:AsyncSession=Depends(get_db)):
    #进入请求后先检查用户是否存在，如果不存在，提示用户进行注册；如果存在，验证密码正确与否，密码正确就生成访问令牌，返回响应结果；如果不对则提示用户
    user=await users.authentication_user(db, user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    user_token=await users.create_token(db, user.id)
    response_data=UserAuthResponse(token=user_token,userInfo=UserInfoResponse.model_validate(user))
    return   success_response(message="登录成功!",data=response_data)
#  3 获取用户信息
@api_router.get("/info")
async def get_user_info(user:UserRequestModel=Depends(get_current_user)):
    """
    先从前端的请求头中获取访问令牌，然后验证访问令牌的正确性，如果正确且未过期则返回用户信息，查找对应的用户，如果用户存在则返回用户信息，否则返回错误信息
    此处采用依赖注入的方式
    """

    return success_response(message="获取用户信息成功!",data=UserInfoResponse.model_validate(user))

#4 更新用户信息
#
@api_router.put("/update")
async def update_user_info(user_data:UserInfoUpdate,db:AsyncSession=Depends(get_db),user:UserRequestModel=Depends(get_current_user)):
    user=await users.update_user_info(db,user.username,user_data)
    return   success_response(message="更新成功",data=UserInfoResponse.model_validate(user))

# #5 修改用户密码
@api_router.put("/password")
async def update_user_password(password_data:PasswordUpdate,db:AsyncSession=Depends(get_db),user:UserRequestModel=Depends(get_current_user)):
    update_result=await users.update_user_password(db, user, password_data.new_password, password_data.old_password)
    if not update_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码更新失败")
    return    success_response(message="密码修改成功")
