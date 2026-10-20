from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict

from schemas.base import NewsItemBase

class AddHistoryRequestResponse(BaseModel):
    news_id:int=Field(...,alias="newsId")
   # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,#alias 字段名称兼容
        from_attributes=True#设置允许从orm对象属性中取值
    )

class HistoryRequestResponse(BaseModel):
    id:int = Field(...)
    user_id:int=Field(...,alias="userId")
    news_id:int=Field(...,alias="newsId")
    views_time:datetime = Field(...,alias="viewsTime")
   # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,#alias 字段名称兼容
        from_attributes=True#设置允许从orm对象属性中取值

    )

class HistoryNewsItemResponse(NewsItemBase):
    view_time: datetime = Field(..., alias="viewTime")
    # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias 字段名称兼容
        from_attributes=True  # 设置允许从orm对象属性中取值
    )

class HistoryListRequestResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")
    # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias 字段名称兼容
        from_attributes=True  # 设置允许从orm对象属性中取值
    )
