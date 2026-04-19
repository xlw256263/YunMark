# back/app/api/v1/admin_shares.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.bookmark_share import (
    AdminReviewRequest,
    BookmarkShareResponse,
    BookmarkShareListResponse
)
from app.dependencies import get_current_active_user
from app.services.bookmark_share_service import BookmarkShareService

router = APIRouter(prefix="/admin/shares", tags=["管理员-分享审核"])


def verify_admin(user: User):
    """验证管理员权限"""
    if user.role != "admin":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.get("/pending", response_model=BookmarkShareListResponse, summary="获取待审核列表")
async def get_pending_shares(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        status: Optional[str] = Query(None, description="状态过滤：pending/reviewing"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    管理员获取待审核的分享列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **status**: 可选，按状态过滤
    """
    admin_user = verify_admin(current_user)

    return BookmarkShareService.admin_get_pending_shares(
        db=db,
        page=page,
        page_size=page_size,
        status_filter=status
    )


@router.post("/review", response_model=BookmarkShareResponse, summary="审核分享")
async def review_share(
        review_data: AdminReviewRequest,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    管理员审核分享（通过或驳回）

    - **share_id**: 分享记录ID
    - **status**: 审核结果（approved/rejected）
    - **review_note**: 审核备注（可选）
    - **reject_reason**: 驳回原因（status=rejected 时必填）
    """
    admin_user = verify_admin(current_user)

    return BookmarkShareService.admin_review_share(
        db=db,
        admin_user=admin_user,
        review_data=review_data
    )


@router.post("/{share_id}/take-down", response_model=BookmarkShareResponse, summary="下架分享")
async def take_down_share(
        share_id: int,
        reason: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    管理员下架已通过的分享（违规内容）

    - **share_id**: 分享记录ID
    - **reason**: 下架原因
    """
    admin_user = verify_admin(current_user)

    return BookmarkShareService.admin_take_down_share(
        db=db,
        admin_user=admin_user,
        share_id=share_id,
        reason=reason
    )
