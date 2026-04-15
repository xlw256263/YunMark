from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


# 书签-标签关联表（多对多关系）
# 该表用于实现 Bookmark 和 Tag 之间的多对多关系
# 包含两个外键，分别指向 bookmarks 表和 tags 表的主键
bookmark_tag = Table(
    'bookmark_tag',
    Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id'), primary_key=True, comment='书签ID'),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True, comment='标签ID')
)


class Category(Base):
    """
    分类模型
    
    用于对书签进行分类管理，每个分类属于特定用户。
    一个用户可以有多个分类，一个分类可以包含多个书签。
    """
    __tablename__ = "categories"

    # 主键 ID，自增
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='分类ID')
    
    # 分类名称，最大长度100字符，不能为空
    name = Column(String(100), nullable=False, comment='分类名称')
    
    # 所属用户ID，外键关联 users 表，不能为空，建立索引以提高查询效率
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='所属用户ID')

    # 关系定义
    # 与 Bookmark 的一对多关系：一个分类下有多个书签
    bookmarks = relationship("Bookmark", back_populates="category")
    
    # 与 User 的多对一关系：一个分类属于一个用户
    user = relationship("User", back_populates="categories")

    def __repr__(self):
        """返回分类对象的字符串表示，便于调试和日志记录"""
        return f"<Category(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Tag(Base):
    """
    标签模型
    
    用于给书签打标签，支持灵活的多维度分类。
    标签名称全局唯一，一个标签可以被多个书签使用，一个书签也可以有多个标签。
    """
    __tablename__ = "tags"

    # 主键 ID，自增
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='标签ID')
    
    # 标签名称，最大长度50字符，全局唯一，不能为空，建立索引以加速查找
    name = Column(String(50), unique=True, nullable=False, index=True, comment='标签名称')

    # 关系定义
    # 与 Bookmark 的多对多关系：通过 bookmark_tag 关联表实现
    # secondary 参数指定了关联表，back_populates 确保双向同步
    bookmarks = relationship("Bookmark", secondary=bookmark_tag, back_populates="tags")

    def __repr__(self):
        """返回标签对象的字符串表示，便于调试和日志记录"""
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Bookmark(Base):
    """
    书签模型
    
    核心业务模型，存储用户保存的网页书签信息。
    支持分类、标签、点击统计等功能。
    """
    __tablename__ = "bookmarks"

    # 主键 ID，自增
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='书签ID')
    
    # 所属用户ID，外键关联 users 表，不能为空，建立索引以加速按用户查询
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='所属用户ID')
    
    # 所属分类ID，外键关联 categories 表，可为空（允许无分类），建立索引
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True, index=True, comment='所属分类ID')
    
    # 书签URL，最大长度2048字符，不能为空
    url = Column(String(2048), nullable=False, comment='书签URL地址')
    
    # 书签标题，最大长度500字符，不能为空
    title = Column(String(500), nullable=False, comment='书签标题')
    
    # 书签描述，文本类型，可为空
    description = Column(Text, nullable=True, comment='书签描述')
    
    # 网站图标URL，最大长度500字符，可为空
    favicon = Column(String(500), nullable=True, comment='网站图标URL')
    
    # 点击次数，默认为0，用于统计书签受欢迎程度
    click_count = Column(Integer, default=0, comment='点击次数')
    
    # 创建时间，默认为当前UTC时间
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系定义
    # 与 User 的多对一关系：一个书签属于一个用户
    user = relationship("User", back_populates="bookmarks")
    
    # 与 Category 的多对一关系：一个书签属于一个分类（可选）
    category = relationship("Category", back_populates="bookmarks")
    
    # 与 Tag 的多对多关系：一个书签可以有多个标签，通过 bookmark_tag 关联表实现
    tags = relationship("Tag", secondary=bookmark_tag, back_populates="bookmarks")

    def __repr__(self):
        """返回书签对象的字符串表示，便于调试和日志记录"""
        return f"<Bookmark(id={self.id}, title='{self.title}', url='{self.url}')>"
