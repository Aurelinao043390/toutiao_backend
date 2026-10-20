from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import Request
from fastapi.responses import JSONResponse
from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, general_exception_handler
def register_exception_handlers(app):
    """
    注册全局异常处理，统一返回格式，子类在前面，父类在后面；具体在前面，抽象在后面
    """
    #业务层面
    app.add_exception_handler(HTTPException, http_exception_handler)
    #数据完整性层面
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    # 数据库层面
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    # 其他层面。兜底默认
    app.add_exception_handler(Exception, general_exception_handler)
