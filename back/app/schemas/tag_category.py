from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TagCategoryBase(BaseModel):
    """
    标签分类基础数据模型
    """
    name: str  # 分类名称
    description: Optional[str] = None  # 分类描述
    sort_order: int = 0  # 排序顺序

    class Config:
        json_schema_extra = {
            "example": {
                "name": "编程语言",
                "description": "各种编程相关的标签",
                "sort_order": 1
            }
        }


class TagCategoryCreate(TagCategoryBase):
    """
    创建标签分类请求模型
    """
    pass


class TagCategoryUpdate(BaseModel):
    """
    更新标签分类请求模型
    """
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class TagCategoryResponse(TagCategoryBase):
    """
    标签分类响应模型
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

