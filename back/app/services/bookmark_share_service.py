# back/app/services/bookmark_share_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.bookmark_share import BookmarkShare, ShareStatus
from app.models.bookmark import Bookmark
from app.models.user import User
from app.schemas.bookmark_share import (
    BookmarkShareCreate,
    AdminReviewRequest,
    BookmarkShareResponse
)


class BookmarkShareService:
    """书签分享服务类"""

    @staticmethod
    def create_share(db: Session, user_id: int, bookmark_id: int) -> BookmarkShare:
        """
        创建分享记录（草稿状态）

        Args:
            db: 数据库会话
            user_id: 用户ID
            bookmark_id: 书签ID

        Returns:
            创建的分享记录

        Raises:
            HTTPException: 书签不存在或不属于当前用户
        """
        # 验证书签是否存在且属于当前用户
        bookmark = db.query(Bookmark).filter(
            and_(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == user_id
            )
        ).first()

        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found or access denied"
            )

        # 检查是否已有待审核或已通过的分享记录
        existing_share = db.query(BookmarkShare).filter(
            and_(
                BookmarkShare.bookmark_id == bookmark_id,
                BookmarkShare.status.in_([
                    ShareStatus.PENDING,
                    ShareStatus.REVIEWING,
                    ShareStatus.APPROVED
                ])
            )
        ).first()

        if existing_share:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Bookmark already has an active share (status: {existing_share.status.value})"
            )

        # 创建新的分享记录（草稿状态）
        new_share = BookmarkShare(
            bookmark_id=bookmark_id,
            user_id=user_id,
            status=ShareStatus.DRAFT
        )

        db.add(new_share)
        db.commit()
        db.refresh(new_share)

        return new_share

    @staticmethod
    def submit_for_review(db: Session, user_id: int, share_id: int) -> BookmarkShare:
        """
        提交分享审核

        Args:
            db: 数据库会话
            user_id: 用户ID
            share_id: 分享记录ID

        Returns:
            更新后的分享记录
        """
        share = db.query(BookmarkShare).filter(
            and_(
                BookmarkShare.id == share_id,
                BookmarkShare.user_id == user_id
            )
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share record not found or access denied"
            )

        if share.status != ShareStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit share with status: {share.status.value}"
            )

        # 黑名单校验：检查书签 URL 是否在黑名单中
        from app.models.blacklist import Blacklist

        bookmark = share.bookmark
        if bookmark:
            blacklist_items = db.query(Blacklist).all()
            for item in blacklist_items:
                if item.pattern.lower() in bookmark.url.lower():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"该书签 URL 被系统限制：{item.pattern}。{item.description or '无法分享此链接'}"
                    )

        # 更新状态为待审核
        share.status = ShareStatus.PENDING
        share.submitted_at = datetime.utcnow()

        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def cancel_share(db: Session, user_id: int, share_id: int) -> BookmarkShare:
        """
        取消分享

        Args:
            db: 数据库会话
            user_id: 用户ID
            share_id: 分享记录ID

        Returns:
            更新后的分享记录
        """
        share = db.query(BookmarkShare).filter(
            and_(
                BookmarkShare.id == share_id,
                BookmarkShare.user_id == user_id
            )
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share record not found or access denied"
            )

        if share.status in [ShareStatus.APPROVED, ShareStatus.TAKEN_DOWN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel share with status: {share.status.value}"
            )

        # 更新状态为已取消
        share.status = ShareStatus.CANCELLED

        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def get_user_shares(
            db: Session,
            user_id: int,
            page: int = 1,
            page_size: int = 10,
            status_filter: Optional[str] = None
    ) -> dict:
        """
        获取用户的分享列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            status_filter: 状态过滤（可选）

        Returns:
            分页的分享列表
        """
        query = db.query(BookmarkShare).filter(
            BookmarkShare.user_id == user_id
        )

        # 状态过滤
        if status_filter:
            try:
                status_enum = ShareStatus(status_filter)
                query = query.filter(BookmarkShare.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )

        # 总数
        total = query.count()

        # 分页查询
        shares = query.order_by(desc(BookmarkShare.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        # 构建响应数据
        items = []
        for share in shares:
            bookmark = share.bookmark
            user = share.user
            reviewer = share.reviewer

            item = BookmarkShareResponse(
                id=share.id,
                bookmark_id=share.bookmark_id,
                user_id=share.user_id,
                status=share.status,
                review_note=share.review_note,
                reject_reason=share.reject_reason,
                submitted_at=share.submitted_at,
                reviewed_at=share.reviewed_at,
                reviewer_id=share.reviewer_id,
                created_at=share.created_at,
                updated_at=share.updated_at,
                bookmark_title=bookmark.title if bookmark else None,
                bookmark_url=bookmark.url if bookmark else None,
                bookmark_description=bookmark.description if bookmark else None,
                bookmark_favicon=bookmark.favicon if bookmark else None,
                username=user.username if user else None,
                reviewer_username=reviewer.username if reviewer else None
            )
            items.append(item)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    @staticmethod
    def admin_get_pending_shares(
            db: Session,
            page: int = 1,
            page_size: int = 20,
            status_filter: Optional[str] = None
    ) -> dict:
        """
        管理员获取待审核分享列表

        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            status_filter: 状态过滤（默认 pending）

        Returns:
            分页的分享列表
        """
        query = db.query(BookmarkShare)

        # 默认只显示待审核和审核中的
        if status_filter:
            try:
                status_enum = ShareStatus(status_filter)
                query = query.filter(BookmarkShare.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        else:
            query = query.filter(
                BookmarkShare.status.in_([
                    ShareStatus.PENDING,
                    ShareStatus.REVIEWING
                ])
            )

        total = query.count()

        shares = query.order_by(desc(BookmarkShare.submitted_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        items = []
        for share in shares:
            bookmark = share.bookmark
            user = share.user

            item = BookmarkShareResponse(
                id=share.id,
                bookmark_id=share.bookmark_id,
                user_id=share.user_id,
                status=share.status,
                review_note=share.review_note,
                reject_reason=share.reject_reason,
                submitted_at=share.submitted_at,
                reviewed_at=share.reviewed_at,
                reviewer_id=share.reviewer_id,
                created_at=share.created_at,
                updated_at=share.updated_at,
                bookmark_title=bookmark.title if bookmark else None,
                bookmark_url=bookmark.url if bookmark else None,
                bookmark_description=bookmark.description if bookmark else None,
                bookmark_favicon=bookmark.favicon if bookmark else None,
                username=user.username if user else None,
                reviewer_username=None
            )
            items.append(item)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    @staticmethod
    def admin_review_share(
            db: Session,
            admin_user: User,
            review_data: AdminReviewRequest
    ) -> BookmarkShare:
        """
        管理员审核分享

        Args:
            db: 数据库会话
            admin_user: 管理员用户对象
            review_data: 审核数据

        Returns:
            更新后的分享记录
        """
        share = db.query(BookmarkShare).filter(
            BookmarkShare.id == review_data.share_id
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share record not found"
            )

        if share.status not in [ShareStatus.PENDING, ShareStatus.REVIEWING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot review share with status: {share.status.value}"
            )

        # 验证审核状态
        if review_data.status not in [ShareStatus.APPROVED, ShareStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review status must be 'approved' or 'rejected'"
            )

        # 如果驳回，必须提供驳回原因
        if review_data.status == ShareStatus.REJECTED and not review_data.reject_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reject reason is required when rejecting a share"
            )

        # 更新分享记录
        share.status = review_data.status
        share.review_note = review_data.review_note
        share.reject_reason = review_data.reject_reason
        share.reviewed_at = datetime.utcnow()
        share.reviewer_id = admin_user.id

        # 如果审核通过，创建官方快照
        if review_data.status == ShareStatus.APPROVED:
            from app.models.official_share_snapshot import OfficialShareSnapshot
            
            bookmark = share.bookmark
            user = share.user
            
            # 构建书签快照（只保留公开信息）
            bookmark_snapshot = {
                "id": bookmark.id,
                "title": bookmark.title,
                "url": bookmark.url,
                "description": bookmark.description,
                "favicon": bookmark.favicon,
                "click_count": bookmark.click_count
            }
            
            # 构建用户快照（脱敏处理，不暴露敏感信息）
            user_snapshot = {
                "username": user.username,
                "avatar_url": user.avatar
            } if user else None
            
            # 创建快照记录
            snapshot = OfficialShareSnapshot(
                share_id=share.id,
                bookmark_snapshot=bookmark_snapshot,
                user_snapshot=user_snapshot,
                curated_at=datetime.utcnow(),
                curator_id=admin_user.id,
                featured_level=0,  # 默认为普通级别
                sort_weight=0,
                is_visible=1
            )
            
            db.add(snapshot)

        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def admin_take_down_share(
            db: Session,
            admin_user: User,
            share_id: int,
            reason: str
    ) -> BookmarkShare:
        """
        管理员下架已通过的分享

        Args:
            db: 数据库会话
            admin_user: 管理员用户对象
            share_id: 分享记录ID
            reason: 下架原因

        Returns:
            更新后的分享记录
        """
        share = db.query(BookmarkShare).filter(
            BookmarkShare.id == share_id
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share record not found"
            )

        if share.status != ShareStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only take down approved shares"
            )

        share.status = ShareStatus.TAKEN_DOWN
        share.reject_reason = reason
        share.reviewed_at = datetime.utcnow()
        share.reviewer_id = admin_user.id

        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def get_approved_shares(
            db: Session,
            page: int = 1,
            page_size: int = 20,
            sort: str = "latest"
    ) -> dict:
        """
        获取已通过的公开分享列表（从快照表读取）

        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            sort: 排序方式（latest/popular/featured）

        Returns:
            分页的分享列表
        """
        from app.models.official_share_snapshot import OfficialShareSnapshot
        
        # 从快照表查询可见的记录
        query = db.query(OfficialShareSnapshot).filter(
            OfficialShareSnapshot.is_visible == 1
        )

        # 排序
        if sort == "popular":
            # 按书签点击量排序（从快照中提取）
            # 注意：MySQL JSON 字段排序需要使用 func.json_extract
            from sqlalchemy import func
            query = query.order_by(
                desc(func.json_extract(OfficialShareSnapshot.bookmark_snapshot, '$.click_count'))
            )
        elif sort == "featured":
            # 按推荐等级和权重排序
            query = query.order_by(
                desc(OfficialShareSnapshot.featured_level),
                desc(OfficialShareSnapshot.sort_weight),
                desc(OfficialShareSnapshot.curated_at)
            )
        else:
            # 默认按收录时间排序（最新通过的在前）
            query = query.order_by(desc(OfficialShareSnapshot.curated_at))

        total = query.count()

        snapshots = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for snapshot in snapshots:
            bookmark_data = snapshot.bookmark_snapshot
            user_data = snapshot.user_snapshot
            
            item = BookmarkShareResponse(
                id=snapshot.id,
                bookmark_id=bookmark_data.get("id"),
                user_id=None,  # 快照中不暴露真实用户ID
                status=ShareStatus.APPROVED,
                review_note=None,
                reject_reason=None,
                submitted_at=None,
                reviewed_at=snapshot.curated_at,
                reviewer_id=None,
                created_at=snapshot.created_at,
                updated_at=snapshot.updated_at,
                bookmark_title=bookmark_data.get("title"),
                bookmark_url=bookmark_data.get("url"),
                bookmark_description=bookmark_data.get("description"),
                bookmark_favicon=bookmark_data.get("favicon"),
                username=user_data.get("username") if user_data else "匿名用户",
                reviewer_username=None
            )
            items.append(item)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
