from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users


async def get_current_user(
        authorization: str=Header(...,alias="Authorization"),
        db:AsyncSession=Depends(get_db)
    ):
    """
    整合 根据token查询用户，返回用户信息
    """
    #Bearer xxxxx 这是前端传过来的token信息，后面xxxx部分就是具体的token的内容
    #第一种写法
    # token=authorization.split(" ")[1]
    #第二种写法
    token=authorization.replace("Bearer ","")
    user=await users.get_user_by_token(db,token)
    if user is None:
        raise HTTPException(status_code=401,detail="无效的令牌或者已过期")
    return user