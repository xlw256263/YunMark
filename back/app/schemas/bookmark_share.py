# back/app/schemas/bookmark_share.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ShareStatusEnum(str, Enum):
    """分享状态枚举（用于 API 文档）"""
    DRAFT = "draft"
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TAKEN_DOWN = "taken_down"


class BookmarkShareCreate(BaseModel):
    """创建分享请求模型"""
    bookmark_id: int = Field(..., description="书签ID")

    class Config:
        json_schema_extra = {
            "example": {
                "bookmark_id": 1
            }
        }


class BookmarkShareSubmit(BaseModel):
    """提交审核请求模型"""
    share_id: int = Field(..., description="分享记录ID")

    class Config:
        json_schema_extra = {
            "example": {
                "share_id": 1
            }
        }


class BookmarkShareCancel(BaseModel):
    """取消分享请求模型"""
    share_id: int = Field(..., description="分享记录ID")


class AdminReviewRequest(BaseModel):
    """管理员审核请求模型"""
    share_id: int = Field(..., description="分享记录ID")
    status: ShareStatusEnum = Field(..., description="审核结果：approved 或 rejected")
    review_note: Optional[str] = Field(None, description="审核备注")
    reject_reason: Optional[str] = Field(None, description="驳回原因（status=rejected 时必填）")

    class Config:
        json_schema_extra = {
            "example": {
                "share_id": 1,
                "status": "approved",
                "review_note": "内容优质，予以通过"
            }
        }


class BookmarkShareResponse(BaseModel):
    """分享记录响应模型"""
    id: int
    bookmark_id: int
    user_id: Optional[int] = None  # 改为可选字段
    status: ShareStatusEnum
    review_note: Optional[str] = None
    reject_reason: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # 嵌套的书签信息
    bookmark_title: Optional[str] = None
    bookmark_url: Optional[str] = None
    bookmark_description: Optional[str] = None
    bookmark_favicon: Optional[str] = None

    # 用户信息
    username: Optional[str] = None

    # 审核人信息
    reviewer_username: Optional[str] = None

    class Config:
        from_attributes = True


class BookmarkShareListResponse(BaseModel):
    """分享列表响应模型（分页）"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[BookmarkShareResponse] = Field(..., description="分享记录列表")
