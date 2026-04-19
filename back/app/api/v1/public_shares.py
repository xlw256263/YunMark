# back/app/api/v1/public_shares.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.bookmark_share import BookmarkShareListResponse
from app.services.bookmark_share_service import BookmarkShareService

router = APIRouter(prefix="/public/shares", tags=["公开分享"])


@router.get("", response_model=BookmarkShareListResponse, summary="获取官方分享列表")
async def get_approved_shares(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        sort: str = Query("latest", description="排序方式：latest（最新）/ popular（热门）"),
        db: Session = Depends(get_db)
):
    """
    获取已通过审核的公开分享列表（无需登录）

    - **page**: 页码
    - **page_size**: 每页数量
    - **sort**: 排序方式
      - `latest`: 按审核时间倒序（最新通过的在前）
      - `popular`: 按书签点击量倒序（最热门的在前）
    """
    return BookmarkShareService.get_approved_shares(
        db=db,
        page=page,
        page_size=page_size,
        sort=sort
    )
