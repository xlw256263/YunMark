from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# 导入数据库会话获取函数，用于在每个请求中创建独立的数据库会话
from app.db.database import get_db
# 导入用户模型，用于类型提示和获取当前用户信息
from app.models.user import User
# 导入书签、分类、标签相关的 Pydantic 模式（Schemas）
# 这些模式用于请求体的验证和响应数据的序列化/反序列化
from app.schemas.bookmark import (
    BookmarkCreate, BookmarkUpdate, BookmarkResponse, BookmarkListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TagCreate, TagResponse, ClickCountResponse
)
# 导入依赖项，用于获取当前激活的用户，实现身份验证和授权
from app.dependencies import get_current_active_user
# 导入业务逻辑服务层，将具体的数据处理逻辑与 API 路由分离，遵循单一职责原则
from app.services.bookmark_service import BookmarkService, CategoryService, TagService

# 创建 API 路由器，设置统一前缀 "/bookmarks" 和标签 "收藏夹"
# 这有助于在 Swagger UI 中对接口进行分组和管理
router = APIRouter(prefix="/bookmarks", tags=["收藏夹"])


# ============ 书签相关 API ============

@router.get("", response_model=BookmarkListResponse, summary="获取书签列表")
async def list_bookmarks(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        category_id: Optional[int] = Query(None, description="按分类过滤"),
        tag_ids: Optional[List[int]] = Query(None, description="按标签过滤"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的书签列表

    - **page**: 页码（从1开始），默认值为1，最小值为1
    - **page_size**: 每页数量（1-100），默认值为10，限制最大值为100以防止过度查询
    - **category_id**: 可选，按分类ID过滤，若提供则只返回该分类下的书签
    - **tag_ids**: 可选，按标签ID列表过滤，支持多标签筛选
    - **current_user**: 通过依赖注入获取当前登录用户，确保数据隔离
    - **db**: 通过依赖注入获取数据库会话
    
    为何如此做：
    1. 使用 Query 参数进行分页和过滤，符合 RESTful API 设计规范，便于前端调用和缓存。
    2. 限制 page_size 的最大值是为了保护后端性能，防止恶意请求导致数据库负载过高。
    3. 依赖注入 current_user 确保只有认证用户才能访问其私有数据，保障安全性。
    4. 调用 Service 层处理业务逻辑，保持路由函数简洁，便于测试和维护。
    """
    return BookmarkService.get_bookmarks(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        category_id=category_id,
        tag_ids=tag_ids
    )


@router.post("", response_model=BookmarkResponse, summary="创建书签")
async def create_bookmark(
        bookmark_data: BookmarkCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    创建新书签

    - **url**: 书签URL（必填），需符合 URL 格式
    - **title**: 书签标题（必填），用于显示
    - **description**: 描述（可选），提供更多上下文
    - **favicon**: 图标URL（可选），用于前端展示
    - **category_id**: 分类ID（可选），关联到特定分类
    - **tag_ids**: 标签ID列表（可选），用于多维度标记
    
    为何如此做：
    1. 使用 POST 方法创建资源，符合 HTTP 语义。
    2. 请求体使用 BookmarkCreate 模式进行严格验证，确保数据完整性。
    3. 自动关联当前用户 ID，防止用户越权创建属于他人的书签。
    4. 返回创建的书签对象，方便前端立即更新界面。
    """
    return BookmarkService.create_bookmark(
        db=db,
        user_id=current_user.id,
        bookmark_data=bookmark_data
    )


@router.get("/{bookmark_id}", response_model=BookmarkResponse, summary="获取单个书签")
async def get_bookmark(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    根据ID获取单个书签详情
    
    为何如此做：
    1. 使用路径参数 {bookmark_id} 定位特定资源。
    2. 在 Service 层内部会校验该书签是否属于当前用户，确保数据安全。
    3. 使用 from_orm 将 ORM 模型转换为 Pydantic 模型，以便序列化为 JSON 响应。
    """
    return BookmarkResponse.from_orm(
        BookmarkService.get_bookmark_by_id(db, bookmark_id, current_user.id)
    )


@router.put("/{bookmark_id}", response_model=BookmarkResponse, summary="更新书签")
async def update_bookmark(
        bookmark_id: int,
        update_data: BookmarkUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新书签信息

    所有字段都是可选的，只更新提供的字段
    
    为何如此做：
    1. 使用 PUT 方法进行全量或增量更新（取决于 Service 层实现，通常 PATCH 更适合增量，但此处统一定义为 PUT）。
    2. BookmarkUpdate 模式中所有字段均为 Optional，允许部分更新。
    3. 同样需要校验用户权限，确保只能修改自己的书签。
    """
    return BookmarkService.update_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=current_user.id,
        update_data=update_data
    )


@router.delete("/{bookmark_id}", summary="删除书签")
async def delete_bookmark(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    删除指定书签
    
    为何如此做：
    1. 使用 DELETE 方法移除资源。
    2. 不返回具体对象，仅返回成功消息，减少网络传输开销。
    3. Service 层会处理级联删除或关联清理（如解除标签关联等）。
    """
    BookmarkService.delete_bookmark(db, bookmark_id, current_user.id)
    return {"message": "Bookmark deleted successfully"}


@router.patch("/{bookmark_id}/click", response_model=ClickCountResponse, summary="增加点击次数")
async def increment_click_count(
        bookmark_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    增加书签的点击次数

    每次调用此接口，点击次数会+1
    
    为何如此做：
    1. 使用 PATCH 方法表示对资源的部分修改（仅修改点击计数）。
    2. 专门的路由用于统计行为，避免与主业务更新逻辑耦合。
    3. 返回更新后的点击次数，方便前端实时反馈。
    """
    return BookmarkService.increment_click_count(db, bookmark_id, current_user.id)


# ============ 分类相关 API ============

@router.get("/categories/list", response_model=List[CategoryResponse], summary="获取分类列表")
async def list_categories(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的所有分类
    
    为何如此做：
    1. 分类是用户个性化的，因此需要传入 current_user 进行过滤。
    2. 返回 List[CategoryResponse]，直接序列化列表数据。
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
    
    为何如此做：
    1. 允许用户自定义分类体系，提高书签管理的灵活性。
    2. 关联当前用户，确保分类私有性。
    """
    return CategoryService.create_category(db, current_user.id, category_data)


@router.put("/categories/{category_id}", response_model=CategoryResponse, summary="更新分类")
async def update_category(
        category_id: int,
        update_data: CategoryUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新分类名称
    
    为何如此做：
    1. 允许用户重命名分类，提升用户体验。
    2. 校验 category_id 归属权，防止篡改他人分类。
    """
    return CategoryService.update_category(db, category_id, current_user.id, update_data)


@router.delete("/categories/{category_id}", summary="删除分类")
async def delete_category(
        category_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    删除指定分类
    
    为何如此做：
    1. 删除分类时，Service 层通常会处理该分类下书签的归属问题（如移至默认分类或取消分类）。
    2. 确保操作的安全性，仅限所有者删除。
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
    
    为何如此做：
    1. 标签设计为全局共享资源，不同用户可以复用相同的标签，促进标准化。
    2. 不需要 current_user 依赖，因为标签库是公共的。
    3. 用于前端自动补全或标签选择器。
    """
    return TagService.get_all_tags(db)


@router.post("/tags", response_model=TagResponse, summary="创建标签")
async def create_tag(
        tag_data: TagCreate,
        db: Session = Depends(get_db)
):
    """
    创建新标签（如果已存在则返回现有标签）
    
    为何如此做：
    1. 幂等性设计：如果标签已存在，直接返回现有对象，避免重复数据。
    2. 全局标签无需绑定特定用户，任何用户都可以贡献新标签到公共池。
    3. 简化前端逻辑，无需先检查是否存在再创建。
    """
    return TagService.create_tag(db, tag_data)
