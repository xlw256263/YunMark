# back/app/api/v1/shares.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.bookmark_share import (
    BookmarkShareCreate,
    BookmarkShareSubmit,
    BookmarkShareCancel,
    BookmarkShareResponse,
    BookmarkShareListResponse
)
from app.dependencies import get_current_active_user
from app.services.bookmark_share_service import BookmarkShareService

router = APIRouter(prefix="/shares", tags=["书签分享"])


@router.post("", response_model=BookmarkShareResponse, summary="创建分享（草稿）")
async def create_share(
        share_data: BookmarkShareCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    为指定书签创建分享记录（初始状态为草稿）

    - **bookmark_id**: 要分享的书签ID（必须是当前用户的书签）
    """
    return BookmarkShareService.create_share(
        db=db,
        user_id=current_user.id,
        bookmark_id=share_data.bookmark_id
    )


@router.post("/submit", response_model=BookmarkShareResponse, summary="提交审核")
async def submit_for_review(
        submit_data: BookmarkShareSubmit,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    将草稿状态的分享提交审核

    - **share_id**: 分享记录ID
    """
    return BookmarkShareService.submit_for_review(
        db=db,
        user_id=current_user.id,
        share_id=submit_data.share_id
    )


@router.post("/cancel", response_model=BookmarkShareResponse, summary="取消分享")
async def cancel_share(
        cancel_data: BookmarkShareCancel,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    取消分享（仅限草稿、待审核、审核中状态）

    - **share_id**: 分享记录ID
    """
    return BookmarkShareService.cancel_share(
        db=db,
        user_id=current_user.id,
        share_id=cancel_data.share_id
    )


@router.get("/my-shares", response_model=BookmarkShareListResponse, summary="获取我的分享列表")
async def get_my_shares(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        status: Optional[str] = Query(None,
                                      description="状态过滤：draft/pending/reviewing/approved/rejected/cancelled/taken_down"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的分享列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **status**: 可选，按状态过滤
    """
    return BookmarkShareService.get_user_shares(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status_filter=status
    )
