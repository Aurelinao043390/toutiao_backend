from datetime import datetime

from pydantic import BaseModel,Field,ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite:bool=Field(...,alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    # id:int
    # user_id:int=Field(...,alias="userId")
    news_id:int=Field(...,alias="newsId")
    # created_time:datetime=Field(...,alias="createdTime")
    # #添加模型类的配置
    # model_config = ConfigDict(
    #     populate_by_name=True,#alias 字段名称兼容
    #     from_attributes=True#设置允许从orm对象属性中取值
    #
    # )
#收藏的新闻模型类，继承自最基本的新闻模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id:int=Field(...,alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")
   # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,#alias 字段名称兼容
        from_attributes=True#设置允许从orm对象属性中取值

    )
#定义1个 收藏新闻列表的模型类
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total:int
    has_more:bool=Field(...,alias="hasMore")
    # #添加模型类的配置
    model_config = ConfigDict(
        populate_by_name=True,#alias 字段名称兼容
        from_attributes=True#设置允许从orm对象属性中取值

    )