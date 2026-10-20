from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# 注册/登录接口的请求体模型
class UserRequestModel(BaseModel):
    username:str=Field(description="用户名")
    password:str=Field(description="密码")
# 修改密码接口的请求体模型（文档字段名为 oldPassword/newPassword）
class PasswordUpdate(BaseModel):
    # 更新用户密码接口的请求体
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., alias="newPassword", min_length=6, description="新密码")
# 更新用户信息接口的请求体模型，字段均为可选（对应文档 PUT /api/user/update 的请求参数）
class UserInfoUpdate(BaseModel):
    nickname:str|None=Field(default=None,description="用户昵称")
    avatar:str|None=Field(default=None,description="用户头像url")
    gender:str|None=Field(default=None,description="用户性别")
    bio:str|None=Field(default=None,description="用户签名")
    phone:str|None=Field(default=None,description="用户手机号")

#user_info 字段对应的类 基础类+Info类
class UserInfoBase(BaseModel):
    nickname:Optional[str]=Field(default=None,max_length=50,description="用户昵称")
    avatar:Optional[str]=Field(default=None,max_length=255,description="用户头像url")
    gender:Optional[str]=Field(default=None,max_length=10,description="用户性别")
    bio:Optional[str]=Field(default=None,max_length=500,description="用户签名")

#继承上面的UserInfoBase类
class UserInfoResponse(UserInfoBase):
    id:int
    username:str
    #添加模型类的配置
    model_config = ConfigDict(
        from_attributes=True#设置允许从orm对象属性中取值

    )


#data 数据类型
class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse=Field(...,alias="userInfo")
    #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,#alias 字段名称兼容
        from_attributes=True#设置允许从orm对象属性中取值

    )
