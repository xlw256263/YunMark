from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class TagCategory(Base):
    """
    标签分类模型

    用于对标签进行一级分类，方便管理员管理和用户快速定位标签。
    由管理员统一管理，全局共享。
    """
    __tablename__ = "tag_categories"

    # 主键 ID，自增
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='标签分类ID')

    # 分类名称，最大长度50字符，全局唯一，不能为空
    name = Column(String(50), unique=True, nullable=False, index=True, comment='分类名称')

    # 分类描述，最大长度200字符，可为空
    description = Column(String(200), nullable=True, comment='分类描述')

    # 排序顺序，数值越小越靠前，默认为0
    sort_order = Column(Integer, default=0, comment='排序顺序')

    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系定义
    # 与 Tag 的一对多关系：一个分类下有多个标签
    tags = relationship("Tag", back_populates="category")

    def __repr__(self):
        """返回标签分类对象的字符串表示，便于调试和日志记录"""
        return f"<TagCategory(id={self.id}, name='{self.name}', sort_order={self.sort_order})>"

