from fastapi import APIRouter,Depends,Query,HTTPException
from crud import news,news_cache
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db

# 创建api_router的实例
# prefix 路由前缀
# tags 路由的标签，用于分组显示
api_router = APIRouter(prefix="/api/news", tags=["news"])
# 1. 获取新闻分类列表
@api_router.get("/categories")
async def get_categories(db:AsyncSession=Depends(get_db),skip:int=0,limit:int=100):
  categories=await news_cache.get_categories(db,skip,limit)
  print("+++++++++++++++++++++++router 已执行缓存+++++++++++++++++++++++++")
  print("categories", categories)

  return {
    "code": 200,
    "message": "success",
    "data": categories
  }

# 2. 获取新闻列表
@api_router.get("/list")
async def get_news_list(
        db:AsyncSession=Depends(get_db),
        category_id:int=Query(...,description="分类ID",alias="categoryId"),
        page:int=Query(default=1,description="页码"),
        page_size:int=Query(default=10,le=100,description="每页显示的新闻数量，最大值为100，默认为10",alias="pageSize")
):
  # 使用SQLAlchemy的offset和limit方法实现分页逻辑，
  # offset方法用于跳过指定数量的记录，limit方法用于限制返回的记录数量
  # 通过计算总数量减去已返回的数量，判断是否有更多新闻
  offset=(page-1)*page_size
  news_list=await news_cache.get_news_list(db,category_id,offset,page_size)
  total=await news.get_news_count(db,category_id,offset,page_size)
  has_more  =( offset+len(news_list)) <total

  return {
    "code": 200,
    "message": "success",
    "data": {
      "list": news_list,
      "total": total,
      "hasMore": has_more
    }
  }
# 3. 获取新闻详情
@api_router.get("/detail")
async def get_news_detail(
        db:AsyncSession=Depends(get_db),
        id:int=Query(...,description="新闻ID")
):
  news_detail=await news.get_news_detail(db,id)
  if not news_detail:
    raise HTTPException(status_code=404,detail="News not found")
  views_result=await news.increase_views(db, id)
  if not views_result:
    raise HTTPException(status_code=500,detail="Failed to increase views")
  related_news=await news.get_related_news(db,id,news_detail.category_id)
  return {
    "code": 200,
    "message": "success",
    "data": {
      "id": news_detail.id,
      "title": news_detail.title,
      "content": news_detail.content,
      "image": news_detail.image,
      "author": news_detail.author,
      "publishTime": news_detail.publish_time,
      "categoryId": news_detail.category_id,
      "views": news_detail.views,
      "relatedNews": related_news
    }
  }