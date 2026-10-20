# python.exe -m pip install --upgrade pip
# 安装fastapi的快捷命令
# install "fastapi[standard]"
"""
接口实现流程
1 根据《API接口规范》文档完成模块化路由
2 根据《数据库设计规范》文档定义模型类
3 在crud文件夹中完成CRUD的功能封装
4 在路由处理函数里面调用CRUD功能，响应结果
"""

from fastapi import FastAPI, APIRouter
from routers.news import api_router as news_router
from routers.users import api_router as users_router
from routers.favorite import api_router as favorite_router
from routers.history import api_router as history_router
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handlers import register_exception_handlers

# 创建api的实例
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    #允许的源，开发环境允许所有源访问
    #生产环境则必须指定的源访问
    allow_origins=["*"],
    #允许携带cookie
    allow_credentials=True,
    #允许的请求方法
    allow_methods=["*"],
    #允许的请求头
    allow_headers=["*"],

)
# 注册news、users、favorite的路由实例
app.include_router(news_router)
app.include_router(users_router)
app.include_router(favorite_router)
app.include_router(history_router)
# 注册全局异常处理器
register_exception_handlers(app)
@app.get("/")
async def root():
    return {"message": "Hello World"}
















# 按装订区域中的绿色按钮以运行脚本。
# if __name__ == '__main__':
#     print_hi('PyCharm')


