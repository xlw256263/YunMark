from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class OfficialShareSnapshot(Base):
    """
    官方分享快照模型

    当用户分享通过审核时，自动创建快照记录。
    即使原用户删除账号或书签，官方展示不受影响。
    支持数据脱敏和隐私保护。
    """
    __tablename__ = "official_share_snapshots"

    # 主键 ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='快照ID')

    # 关联的原始分享记录ID
    share_id = Column(Integer, ForeignKey('bookmark_shares.id'), nullable=False, index=True, comment='原始分享ID')

    # 书签数据快照（JSON格式存储关键信息）
    bookmark_snapshot = Column(JSON, nullable=False, comment='书签数据快照: {id, title, url, description, favicon}')

    # 用户信息快照（脱敏处理）
    user_snapshot = Column(JSON, nullable=True, comment='用户信息快照: {username, avatar_url}（已脱敏）')

    # 收录时间（审核通过时间）
    curated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment='收录时间')

    # 运营人员ID（策展人）
    curator_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='运营人员ID')

    # 推荐等级：0-普通 1-精选 2-置顶
    featured_level = Column(Integer, default=0, nullable=False, index=True, comment='推荐等级')

    # 排序权重（用于手动调整展示顺序）
    sort_weight = Column(Integer, default=0, nullable=False, comment='排序权重')

    # 是否公开显示
    is_visible = Column(Integer, default=1, nullable=False, index=True, comment='是否可见: 0-隐藏 1-显示')

    # 下架原因
    takedown_reason = Column(Text, nullable=True, comment='下架原因')

    # 下架时间
    takedown_at = Column(DateTime, nullable=True, comment='下架时间')

    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系定义
    original_share = relationship("BookmarkShare", foreign_keys=[share_id])
    curator = relationship("User", foreign_keys=[curator_id])

    def __repr__(self):
        return f"<OfficialShareSnapshot(id={self.id}, share_id={self.share_id}, level={self.featured_level})>"
