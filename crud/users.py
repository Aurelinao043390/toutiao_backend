import uuid
from datetime import datetime,timedelta
from unittest import result

from fastapi import HTTPException
from sqlalchemy import select,func,update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import add
from schemas.users import UserRequestModel, UserInfoUpdate
from models.users import User,UserToken
from utils import securilty
from utils.securilty import verify_password


async def get_user_by_username(db:AsyncSession,username:str) -> User | None:
    """
    根据用户名称查询数据库
    """
    query=select(User).where(User.username==username)
    result=await db.execute(query)
    return result.scalar_one_or_none()
async def get_user_by_userid(db:AsyncSession,userid:int) -> User | None:
    """
    根据用户id查询数据库
    """
    query=select(User).where(User.userid==userid)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db:AsyncSession,userdata:UserRequestModel):
    #先对密码进行加密 pip install passlib[bcrypt]==1.7.4 使用官方推荐的稳定版
    hash_password=securilty.get_hash_password(userdata.password)
    user=User(username=userdata.username,password=hash_password)
    db.add(user)
    await db.commit()
    # 刷新一下，确保拿到是最新数据
    await db.refresh(user)
    return user
#生成token
async def create_token(db:AsyncSession,user_id:int):
    #生成token +设置过期时间（7天）->查询数据库中用户是否有token ，有则直接更新，没有就添加
    token=str(uuid.uuid4())
    expires_at= datetime.now() + timedelta(days=7,hours=0,minutes=0,seconds=0)
    query=select(UserToken).where(UserToken.user_id==user_id)
    result=await db.execute(query)
    user_token=result.scalar_one_or_none()
    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
    else:
        user_token=UserToken(token=token,expires_at=expires_at,user_id=user_id)
        db.add(user_token)
        await db.commit()
        # 刷新一下，确保拿到是最新数据
        await db.refresh(user_token)
    return token



async def authentication_user(db:AsyncSession, username: str,password:str):

    """验证用户名对应的明文密码是否与数据库加密的一致"""
    user=await get_user_by_username(db,username)
    if not user:
        return None
    if not securilty.verify_password(password,user.password):
        return None
    return user

async  def get_user_by_token(db:AsyncSession,token:str):
    """
    根据token查询用户，验证token，查询用户

    """
    query=select(UserToken).where(UserToken.token==token)
    result=await  db.execute(query)
    db_token: UserToken | None = result.scalar_one_or_none()
    if db_token is None or db_token.expires_at < datetime.now():
        return None

    query=select(User).where(db_token.user_id==User.id)
    result=await db.execute(query)
    return result.scalar_one_or_none()

async def update_user_info(db:AsyncSession,user_name:str,user_data:UserInfoUpdate):#可以考虑是否能用userid查询，因为user_name可能重复
    """
    更新用户信息
    """
    #user_data是1个Pydantic类型，需要使用**解包得到字典
    query=update(User).where(User.username==user_name).values(user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result=await db.execute(query)
    await db.commit()
    #检查是否更新成功
    if result.rowcount==0:
        raise HTTPException(status_code=404,detail="用户不存在，更新失败")
    #获取更新后的用户信息
    updated_user=await  get_user_by_username(db,user_name)
    return updated_user


async def update_user_password(db:AsyncSession,user:User,new_password:str,old_password:str):
    """
    修改用户密码
    """
    #验证用户输入的旧密码与数据是否一致
    verify_result= verify_password(old_password, user.password)
    if not verify_result:
        raise HTTPException(status_code=401,detail="旧密码错误，更新失败")
    #更新用户密码
    new_hashed_password=securilty.get_hash_password(new_password)
    user.password=new_hashed_password
    await db.commit()
    await db.refresh(user)
    return True
