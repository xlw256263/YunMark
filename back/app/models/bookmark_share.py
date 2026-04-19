from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum


class ShareStatus(str, enum.Enum):
    """分享状态枚举"""
    DRAFT = "draft"              # 草稿
    PENDING = "pending"          # 待审核
    REVIEWING = "reviewing"      # 审核中
    APPROVED = "approved"        # 已通过
    REJECTED = "rejected"        # 已驳回
    CANCELLED = "cancelled"      # 已取消
    TAKEN_DOWN = "taken_down"    # 已下架


class BookmarkShare(Base):
    """
    书签分享模型
    
    独立的分享记录表，实现用户分享、管理员审核的完整流程。
    一个书签可以有多次分享记录（用户可以反复分享/取消）。
    """
    __tablename__ = "bookmark_shares"

    # 主键 ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='分享记录ID')
    
    # 关联的书签ID
    bookmark_id = Column(Integer, ForeignKey('bookmarks.id'), nullable=False, index=True, comment='书签ID')
    
    # 分享用户ID（冗余字段，便于快速查询）
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='分享用户ID')
    
    # 分享状态 - 使用 String 类型而非 SQLEnum，手动管理枚举值
    status = Column(
        String(20),
        default=ShareStatus.DRAFT.value,
        nullable=False,
        index=True,
        comment='分享状态: draft/pending/reviewing/approved/rejected/cancelled/taken_down'
    )
    
    # 审核备注（管理员填写）
    review_note = Column(Text, nullable=True, comment='审核备注')
    
    # 驳回原因
    reject_reason = Column(Text, nullable=True, comment='驳回原因')
    
    # 提交审核时间
    submitted_at = Column(DateTime, nullable=True, comment='提交审核时间')
    
    # 审核时间
    reviewed_at = Column(DateTime, nullable=True, comment='审核时间')
    
    # 审核人ID
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='审核人ID')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系定义
    bookmark = relationship("Bookmark", back_populates="shares")
    user = relationship("User", foreign_keys=[user_id], back_populates="shares")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<BookmarkShare(id={self.id}, bookmark_id={self.bookmark_id}, status='{self.status}')>"
