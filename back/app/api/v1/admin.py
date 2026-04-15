from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.bookmark import TagCreate, TagResponse
from app.schemas.tag_category import (
    TagCategoryCreate,
    TagCategoryUpdate,
    TagCategoryResponse
)
from app.dependencies import get_current_admin_user
from app.services.bookmark_service import AdminTagService
from app.services.tag_category_service import TagCategoryService

# 创建管理员 API 路由器
router = APIRouter(prefix="/admin", tags=["管理员"])


# ============ 标签管理 API ============

@router.get("/tags", response_model=List[TagResponse], summary="获取所有标签（含使用统计）")
async def admin_list_tags(
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员获取所有标签及其使用统计

    - 按使用次数降序排列
    - 仅管理员可访问

    为何如此做：
    1. 使用 get_current_admin_user 依赖确保只有管理员能访问
    2. 返回 usage_count 字段，方便管理员了解标签使用情况
    3. 为后续的标签清理和优化提供数据支持
    """
    return AdminTagService.get_all_tags_with_stats(db)


@router.post("/tags", response_model=TagResponse, summary="创建标签")
async def admin_create_tag(
        tag_data: TagCreate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员创建新标签

    - **name**: 标签名称（必填，全局唯一）

    为何如此做：
    1. 严格模式：如果标签已存在则返回 409 错误，不允许重复
    2. 由管理员统一维护标签库，保证标签体系的规范性
    3. 初始 usage_count 为 0
    """
    return AdminTagService.create_tag(db, tag_data)


@router.put("/tags/{tag_id}", response_model=TagResponse, summary="更新标签")
async def admin_update_tag(
        tag_id: int,
        tag_name: str,
        category_id: Optional[int] = None,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员更新标签

    - **tag_id**: 标签ID
    - **tag_name**: 新标签名称
    - **category_id**: 新分类ID（可选）

    为何如此做：
    1. 允许管理员修正错误的标签名称
    2. 支持修改标签所属分类
    3. 检查名称冲突，避免重复
    """
    return AdminTagService.update_tag(db, tag_id, tag_name, category_id)


@router.delete("/tags/{tag_id}", summary="删除标签")
async def admin_delete_tag(
        tag_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员删除标签（严格模式）

    - **tag_id**: 标签ID

    为何如此做：
    1. 严格模式：如果标签正在被使用（usage_count > 0），禁止删除
    2. 防止误删导致书签数据不完整
    3. 管理员需先解除所有书签的该标签关联后才能删除
    """
    AdminTagService.delete_tag(db, tag_id)
    return {"message": "Tag deleted successfully"}


# ============ 标签分类管理 API ============

@router.get("/tag-categories", response_model=List[TagCategoryResponse], summary="获取所有标签分类")
async def admin_list_tag_categories(
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员获取所有标签分类

    - 按排序顺序返回
    - 仅管理员可访问
    """
    return TagCategoryService.get_all_categories(db)


@router.get("/tag-categories/{category_id}", response_model=TagCategoryResponse, summary="获取标签分类详情")
async def admin_get_tag_category(
        category_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员获取单个标签分类详情

    - **category_id**: 分类ID
    """
    category = TagCategoryService.get_category_by_id(db, category_id)
    return TagCategoryResponse.model_validate(category)


@router.post("/tag-categories", response_model=TagCategoryResponse, summary="创建标签分类")
async def admin_create_tag_category(
        category_data: TagCategoryCreate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员创建新标签分类

    - **name**: 分类名称（必填，全局唯一）
    - **description**: 分类描述（可选）
    - **sort_order**: 排序顺序（可选，默认0）
    """
    return TagCategoryService.create_category(db, category_data)


@router.put("/tag-categories/{category_id}", response_model=TagCategoryResponse, summary="更新标签分类")
async def admin_update_tag_category(
        category_id: int,
        update_data: TagCategoryUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员更新标签分类

    - **category_id**: 分类ID
    - 所有字段可选，支持部分更新
    """
    return TagCategoryService.update_category(db, category_id, update_data)


@router.delete("/tag-categories/{category_id}", summary="删除标签分类")
async def admin_delete_tag_category(
        category_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    管理员删除标签分类（严格模式）

    - **category_id**: 分类ID

    注意：如果分类下有标签，禁止删除
    """
    TagCategoryService.delete_category(db, category_id)
    return {"message": "Tag category deleted successfully"}
