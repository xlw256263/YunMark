from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============ 标签相关 Schemas ============

class TagBase(BaseModel):
    """
    标签基础数据模型
    
    用于定义标签的核心属性，作为创建和响应模型的基类。
    """
    name: str  # 标签名称，例如 "Python", "Web开发"

    class Config:
        # 提供 API 文档中的示例数据，方便前端开发者理解字段格式
        json_schema_extra = {
            "example": {
                "name": "Python"
            }
        }


class TagCreate(TagBase):
    """
    创建标签请求模型
    
    继承自 TagBase，用于接收前端创建新标签时提交的数据。
    目前只需提供标签名称。
    """
    pass


class TagResponse(TagBase):
    """
    标签响应模型
    
    用于向后端返回标签详细信息，包含数据库生成的 ID。
    """
    id: int  # 标签的唯一标识符

    class Config:
        # 允许从 ORM 模型（如 SQLAlchemy 对象）直接转换为 Pydantic 模型
        from_attributes = True


# ============ 分类相关 Schemas ============

class CategoryBase(BaseModel):
    """
    分类基础数据模型
    
    用于定义书签分类的核心属性。
    """
    name: str  # 分类名称，例如 "技术文章", "常用工具"

    class Config:
        # 提供 API 文档中的示例数据
        json_schema_extra = {
            "example": {
                "name": "技术文章"
            }
        }


class CategoryCreate(CategoryBase):
    """
    创建分类请求模型
    
    继承自 CategoryBase，用于接收前端创建新分类时提交的数据。
    """
    pass


class CategoryUpdate(BaseModel):
    """
    更新分类请求模型
    
    用于接收前端更新分类信息时提交的数据。
    所有字段均为可选，支持部分更新。
    """
    name: Optional[str] = None  # 可选的新分类名称


class CategoryResponse(CategoryBase):
    """
    分类响应模型
    
    用于向后端返回分类的详细信息，包含 ID 和所属用户 ID。
    """
    id: int  # 分类的唯一标识符
    user_id: int  # 所属用户的 ID，用于数据隔离

    class Config:
        # 允许从 ORM 模型直接转换
        from_attributes = True


# ============ 书签相关 Schemas ============

class BookmarkBase(BaseModel):
    """
    书签基础数据模型
    
    定义了书签的核心属性，包括 URL、标题、描述等。
    作为创建和响应模型的基类。
    """
    url: str  # 书签链接地址
    title: str  # 书签标题
    description: Optional[str] = None  # 可选的书签描述
    favicon: Optional[str] = None  # 可选的网站图标 URL
    category_id: Optional[int] = None  # 可选的分类 ID，关联到 Category
    tag_ids: Optional[List[int]] = []  # 关联的标签 ID 列表，默认为空列表

    class Config:
        # 提供详细的 API 示例数据
        json_schema_extra = {
            "example": {
                "url": "https://fastapi.tiangolo.com",
                "title": "FastAPI 官方文档",
                "description": "FastAPI 是一个现代、快速（高性能）的 Web 框架",
                "favicon": "https://fastapi.tiangolo.com/img/favicon.png",
                "category_id": 1,
                "tag_ids": [1, 2]
            }
        }


class BookmarkCreate(BookmarkBase):
    """
    创建书签请求模型
    
    继承自 BookmarkBase，用于接收前端创建新书签时提交的完整数据。
    """
    pass


class BookmarkUpdate(BaseModel):
    """
    更新书签请求模型
    
    用于接收前端更新书签信息时提交的数据。
    所有字段均为可选，支持部分更新（Patch 操作）。
    """
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    favicon: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None  # 注意：此处为 None，表示不传则不更新标签


class BookmarkResponse(BookmarkBase):
    """
    书签响应模型
    
    用于向后端返回书签的完整详细信息，包含系统生成的字段及关联对象。
    """
    model_config = ConfigDict(from_attributes=True)  # 允许从对象属性读取
    id: int  # 书签的唯一标识符
    user_id: int  # 所属用户的 ID
    click_count: int  # 书签被点击的次数
    created_at: datetime  # 书签创建时间
    category: Optional[CategoryResponse] = None  # 嵌套的分类详情对象，若无分类则为 None
    tags: List[TagResponse] = []  # 嵌套的标签详情列表，默认为空




class BookmarkListResponse(BaseModel):
    """
    书签列表响应模型
    
    用于分页查询书签列表时的返回结构。
    """
    total: int  # 符合条件的书签总数
    page: int  # 当前页码
    page_size: int  # 每页显示的数量
    items: List[BookmarkResponse]  # 当前页的书签详情列表


class ClickCountResponse(BaseModel):
    """
    点击计数响应模型
    
    用于单独返回书签点击次数更新后的结果。
    """
    bookmark_id: int  # 书签 ID
    click_count: int  # 更新后的点击次数
