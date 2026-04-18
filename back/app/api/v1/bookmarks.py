from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models import Bookmark, Tag
from app.models.user import User
from app.schemas.bookmark import (
    BookmarkCreate, BookmarkUpdate, BookmarkResponse, BookmarkListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TagCreate, TagResponse, ClickCountResponse
)
from app.schemas.tag_category import TagCategoryResponse
from app.dependencies import get_current_active_user
from app.services.bookmark_service import BookmarkService, CategoryService, TagService

router = APIRouter(prefix="/bookmarks", tags=["收藏夹"])


# ============ 书签相关 API ============

@router.get("", response_model=BookmarkListResponse, summary="获取书签列表")
async def list_bookmarks(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        category_id: Optional[int] = Query(None, description="按分类过滤"),
        tag_ids: Optional[List[int]] = Query(default=None, description="按标签过滤"),
        title: Optional[str] = Query(None, description="按标题模糊搜索"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的书签列表
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **category_id**: 按分类ID过滤
    - **tag_ids**: 按标签ID列表过滤（支持多个：?tag_ids=1&tag_ids=2）
    - **title**: 按标题模糊搜索
    """
    # 调试日志
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"收到请求 - tag_ids: {tag_ids}, type: {type(tag_ids)}")
    
    return BookmarkService.get_bookmarks(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        category_id=category_id,
        tag_ids=tag_ids,
        title=title
    )


@router.post("", response_model=BookmarkResponse, summary="创建书签")
async def create_bookmark(
        bookmark_data: BookmarkCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    创建新书签
    """
    return BookmarkService.create_bookmark(
        db=db,
        user_id=current_user.id,
        bookmark_data=bookmark_data
    )


@router.get("/{bookmark_id:int}", response_model=BookmarkResponse, summary="获取单个书签")
async def get_bookmark(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    根据ID获取单个书签详情
    """
    return BookmarkResponse.model_validate(
        BookmarkService.get_bookmark_by_id(db, bookmark_id, current_user.id)
    )


@router.put("/{bookmark_id:int}", response_model=BookmarkResponse, summary="更新书签")
async def update_bookmark(
        bookmark_id: int,
        update_data: BookmarkUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新书签信息（所有字段可选）
    """
    return BookmarkService.update_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=current_user.id,
        update_data=update_data
    )


@router.delete("/{bookmark_id:int}", summary="删除书签")
async def delete_bookmark(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    删除指定书签
    """
    BookmarkService.delete_bookmark(db, bookmark_id, current_user.id)
    return {"message": "Bookmark deleted successfully"}


@router.patch("/{bookmark_id:int}/click", response_model=ClickCountResponse, summary="增加点击次数")
async def increment_click_count(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    增加书签的点击次数
    """
    return BookmarkService.increment_click_count(db, bookmark_id, current_user.id)


# ============ 标签分类相关 API（公开接口，必须在动态路由之前） ============

@router.get("/tag-categories", response_model=List[TagCategoryResponse], summary="获取标签分类列表")
async def list_tag_categories(db: Session = Depends(get_db)):
    """
    获取所有标签分类（公开接口，用于书签选择标签）
    """
    from app.services.tag_category_service import TagCategoryService
    return TagCategoryService.get_all_categories(db)



# ============ 分类相关 API ============

@router.get("/categories/list", response_model=List[CategoryResponse], summary="获取分类列表")
async def list_categories(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的所有分类
    """
    return CategoryService.get_categories(db, current_user.id)


@router.post("/categories", response_model=CategoryResponse, summary="创建分类")
async def create_category(
        category_data: CategoryCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    创建新分类
    """
    return CategoryService.create_category(db, current_user.id, category_data)


@router.put("/categories/{category_id:int}", response_model=CategoryResponse, summary="更新分类")
async def update_category(
        category_id: int,
        update_data: CategoryUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新分类名称
    """
    return CategoryService.update_category(db, category_id, current_user.id, update_data)


@router.delete("/categories/{category_id:int}", summary="删除分类")
async def delete_category(
        category_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    删除指定分类
    """
    CategoryService.delete_category(db, category_id, current_user.id)
    return {"message": "Category deleted successfully"}


# ============ 标签相关 API ============

@router.get("/tags/list", response_model=List[TagResponse], summary="获取所有标签")
async def list_tags(
        db: Session = Depends(get_db)
):
    """
    获取系统中所有标签（全局共享）
    """
    return TagService.get_all_tags(db)


@router.get("/tags/my-tags", response_model=List[TagResponse], summary="获取当前用户使用的标签")
async def get_my_tags(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户书签中使用过的所有标签（去重）
    """
    from app.models.bookmark import bookmark_tag
    from sqlalchemy import distinct
    
    # 查询当前用户书签使用过的所有标签 ID
    tag_ids = db.query(distinct(bookmark_tag.c.tag_id)).join(
        Bookmark, Bookmark.id == bookmark_tag.c.bookmark_id
    ).filter(
        Bookmark.user_id == current_user.id
    ).all()
    
    # 提取标签 ID 列表
    tag_id_list = [row[0] for row in tag_ids]
    
    if not tag_id_list:
        return []
    
    # 查询标签详情
    tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()
    return [TagResponse.model_validate(tag) for tag in tags]


@router.post("/tags", response_model=TagResponse, summary="创建标签")
async def create_tag(
        tag_data: TagCreate,
        db: Session = Depends(get_db)
):
    """
    创建新标签（如果已存在则返回现有标签）
    """
    return TagService.create_tag(db, tag_data)
