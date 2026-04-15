from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from app.models.bookmark import Bookmark, Category, Tag
from app.schemas.bookmark import (
    BookmarkCreate, BookmarkUpdate, BookmarkResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TagCreate, TagResponse, BookmarkListResponse
)
from app.core.exceptions import NotFoundError


class BookmarkService:
    """书签服务类，提供书签的增删改查及统计功能"""

    @staticmethod
    def get_bookmarks(
            db: Session,
            user_id: int,
            page: int = 1,
            page_size: int = 10,
            category_id: Optional[int] = None,
            tag_ids: Optional[List[int]] = None
    ) -> BookmarkListResponse:
        """
        获取书签列表（支持分页和过滤）

        Args:
            db: 数据库会话对象
            user_id: 当前用户ID，用于数据隔离
            page: 页码，默认为1
            page_size: 每页显示数量，默认为10
            category_id: 可选，按分类ID进行过滤
            tag_ids: 可选，按标签ID列表进行过滤（多对多关系）

        Returns:
            BookmarkListResponse: 包含总记录数、当前页码、每页数量及书签列表的响应对象
        """
        # 初始化基础查询，强制限制为当前用户的书签
        query = db.query(Bookmark).filter(Bookmark.user_id == user_id)

        # 如果指定了分类ID，添加分类过滤条件
        if category_id:
            query = query.filter(Bookmark.category_id == category_id)

        # 如果指定了标签ID列表，通过关联表进行过滤
        # 注意：这里 Bookmark.tags 是定义好的多对多关系
        if tag_ids:
            # 通过 join 关联 Bookmark 和 Tag 的多对多关系表
            # 然后过滤出 tag_id 在给定列表中的记录
            # 注意：如果 tag_ids 中有多个 ID，这里会返回包含任意一个指定标签的书签（OR 逻辑）
            query = query.join(Bookmark.tags).filter(Tag.id.in_(tag_ids))

        # 执行计数查询，获取满足条件的总记录数
        total = query.count()

        # 执行分页查询：
        # 1. 按创建时间倒序排列（最新的在前）
        # 2. 计算偏移量 offset
        # 3. 限制返回数量 limit
        bookmarks = query.order_by(Bookmark.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        # 将 ORM 模型对象转换为 Pydantic 响应模型，并构建最终响应
        return BookmarkListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[BookmarkResponse.model_validate(b) for b in bookmarks]
        )

    @staticmethod
    def get_bookmark_by_id(db: Session, bookmark_id: int, user_id: int) -> Bookmark:
        """
        根据ID获取单个书签详情
        
        Args:
            db: 数据库会话对象
            bookmark_id: 书签ID
            user_id: 用户ID，确保只能访问自己的书签

        Returns:
            Bookmark: 书签ORM对象

        Raises:
            NotFoundError: 当书签不存在或不属于当前用户时抛出
        """
        # 查询指定ID且属于当前用户的书签
        bookmark = db.query(Bookmark).filter(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == user_id
        ).first()

        # 如果未找到，抛出404异常
        if not bookmark:
            raise NotFoundError("Bookmark not found")

        return bookmark

    @staticmethod
    def create_bookmark(db: Session, user_id: int, bookmark_data: BookmarkCreate) -> BookmarkResponse:
        """
        创建新书签

        Args:
            db: 数据库会话对象
            user_id: 当前用户ID
            bookmark_data: 包含书签信息的Pydantic模型

        Returns:
            BookmarkResponse: 创建成功后的书签响应对象

        Raises:
            NotFoundError: 如果指定的分类ID存在但不属于当前用户
        """
        # 验证分类是否存在且属于当前用户（如果提供了category_id）
        if bookmark_data.category_id:
            category = db.query(Category).filter(
                Category.id == bookmark_data.category_id,
                Category.user_id == user_id
            ).first()
            if not category:
                raise NotFoundError("Category not found")

        # 实例化书签ORM对象
        db_bookmark = Bookmark(
            user_id=user_id,
            url=bookmark_data.url,
            title=bookmark_data.title,
            description=bookmark_data.description,
            favicon=bookmark_data.favicon,
            category_id=bookmark_data.category_id,
            click_count=0  # 初始点击数为0
        )

        # 如果提供了标签ID列表，关联对应的标签对象
        if bookmark_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(bookmark_data.tag_ids)).all()
            db_bookmark.tags = tags

        # 提交事务到数据库
        db.add(db_bookmark)
        db.commit()
        # 刷新对象以获取数据库生成的默认值（如ID, created_at等）
        db.refresh(db_bookmark)

        return BookmarkResponse.from_orm(db_bookmark)

    @staticmethod
    def update_bookmark(
            db: Session,
            bookmark_id: int,
            user_id: int,
            update_data: BookmarkUpdate
    ) -> BookmarkResponse:
        """
        更新现有书签信息

        Args:
            db: 数据库会话对象
            bookmark_id: 待更新书签的ID
            user_id: 当前用户ID
            update_data: 包含更新字段的Pydantic模型

        Returns:
            BookmarkResponse: 更新后的书签响应对象

        Raises:
            NotFoundError: 如果书签或关联的分类不存在
        """
        # 获取书签对象，若不存在则直接抛出异常
        bookmark = BookmarkService.get_bookmark_by_id(db, bookmark_id, user_id)

        # 获取已设置的更新字段字典，排除未设置的字段
        update_dict = update_data.dict(exclude_unset=True)

        # 处理分类更新逻辑
        if "category_id" in update_dict:
            # 如果设置为新的分类ID，需验证该分类是否属于当前用户
            if update_dict["category_id"]:
                category = db.query(Category).filter(
                    Category.id == update_dict["category_id"],
                    Category.user_id == user_id
                ).first()
                if not category:
                    raise NotFoundError("Category not found")

        # 处理标签更新逻辑
        # 从字典中弹出tag_ids，避免后续setattr报错（因为tags是关系属性而非普通列）
        tag_ids = update_dict.pop("tag_ids", None)
        if tag_ids is not None:
            # 查询对应的标签对象并重新赋值给书签的tags关系
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            bookmark.tags = tags

        # 更新其余普通字段（如title, url, description等）
        for field, value in update_dict.items():
            setattr(bookmark, field, value)

        # 提交更改并刷新对象
        db.commit()
        db.refresh(bookmark)

        return BookmarkResponse.from_orm(bookmark)

    @staticmethod
    def delete_bookmark(db: Session, bookmark_id: int, user_id: int) -> bool:
        """
        删除指定书签

        Args:
            db: 数据库会话对象
            bookmark_id: 待删除书签的ID
            user_id: 当前用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            NotFoundError: 如果书签不存在
        """
        # 获取书签对象（同时验证权限）
        bookmark = BookmarkService.get_bookmark_by_id(db, bookmark_id, user_id)
        
        # 执行删除操作
        db.delete(bookmark)
        db.commit()
        return True

    @staticmethod
    def increment_click_count(db: Session, bookmark_id: int, user_id: int) -> dict:
        """
        增加书签的点击次数

        Args:
            db: 数据库会话对象
            bookmark_id: 书签ID
            user_id: 当前用户ID

        Returns:
            dict: 包含书签ID和最新点击次数的字典

        Raises:
            NotFoundError: 如果书签不存在
        """
        # 获取书签对象
        bookmark = BookmarkService.get_bookmark_by_id(db, bookmark_id, user_id)
        
        # 点击次数加1
        bookmark.click_count += 1
        
        # 提交更新
        db.commit()
        db.refresh(bookmark)

        return {
            "bookmark_id": bookmark.id,
            "click_count": bookmark.click_count
        }


class CategoryService:
    """分类服务类，提供书签分类的管理功能"""

    @staticmethod
    def get_categories(db: Session, user_id: int) -> List[CategoryResponse]:
        """
        获取当前用户的所有书签分类

        Args:
            db: 数据库会话对象
            user_id: 当前用户ID

        Returns:
            List[CategoryResponse]: 分类响应对象列表
        """
        categories = db.query(Category).filter(Category.user_id == user_id).all()
        return [CategoryResponse.from_orm(c) for c in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int, user_id: int) -> Category:
        """
        根据ID获取单个分类详情

        Args:
            db: 数据库会话对象
            category_id: 分类ID
            user_id: 当前用户ID

        Returns:
            Category: 分类ORM对象

        Raises:
            NotFoundError: 如果分类不存在或不属于当前用户
        """
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise NotFoundError("Category not found")

        return category

    @staticmethod
    def create_category(db: Session, user_id: int, category_data: CategoryCreate) -> CategoryResponse:
        """
        创建新分类

        Args:
            db: 数据库会话对象
            user_id: 当前用户ID
            category_data: 包含分类名称的Pydantic模型

        Returns:
            CategoryResponse: 创建成功的分类响应对象
        """
        db_category = Category(
            name=category_data.name,
            user_id=user_id
        )

        db.add(db_category)
        db.commit()
        db.refresh(db_category)

        return CategoryResponse.from_orm(db_category)

    @staticmethod
    def update_category(
            db: Session,
            category_id: int,
            user_id: int,
            update_data: CategoryUpdate
    ) -> CategoryResponse:
        """
        更新分类信息

        Args:
            db: 数据库会话对象
            category_id: 分类ID
            user_id: 当前用户ID
            update_data: 包含更新字段的Pydantic模型

        Returns:
            CategoryResponse: 更新后的分类响应对象

        Raises:
            NotFoundError: 如果分类不存在
        """
        # 获取分类对象
        category = CategoryService.get_category_by_id(db, category_id, user_id)

        # 如果提供了新名称，则更新
        if update_data.name:
            category.name = update_data.name

        db.commit()
        db.refresh(category)

        return CategoryResponse.from_orm(category)

    @staticmethod
    def delete_category(db: Session, category_id: int, user_id: int) -> bool:
        """
        删除分类

        Args:
            db: 数据库会话对象
            category_id: 分类ID
            user_id: 当前用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            NotFoundError: 如果分类不存在
        """
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        db.delete(category)
        db.commit()
        return True


class TagService:
    """标签服务类，提供全局标签的管理功能"""

    @staticmethod
    def get_all_tags(db: Session) -> List[TagResponse]:
        """
        获取系统中所有标签

        Args:
            db: 数据库会话对象

        Returns:
            List[TagResponse]: 标签响应对象列表
        """
        tags = db.query(Tag).all()
        return [TagResponse.from_orm(t) for t in tags]

    @staticmethod
    def get_tag_by_id(db: Session, tag_id: int) -> Tag:
        """
        根据ID获取单个标签

        Args:
            db: 数据库会话对象
            tag_id: 标签ID

        Returns:
            Tag: 标签ORM对象

        Raises:
            NotFoundError: 如果标签不存在
        """
        tag = db.query(Tag).filter(Tag.id == tag_id).first()

        if not tag:
            raise NotFoundError("Tag not found")

        return tag

    @staticmethod
    def get_or_create_tag(db: Session, tag_name: str) -> Tag:
        """
        获取或创建标签（标签通常是全局共享的，避免重复创建）

        Args:
            db: 数据库会话对象
            tag_name: 标签名称

        Returns:
            Tag: 标签ORM对象
        """
        # 尝试查找已存在的标签
        tag = db.query(Tag).filter(Tag.name == tag_name).first()

        # 如果不存在，则创建新标签
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

        return tag

    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> TagResponse:
        """
        显式创建新标签

        Args:
            db: 数据库会话对象
            tag_data: 包含标签名称的Pydantic模型

        Returns:
            TagResponse: 标签响应对象（如果已存在则返回现有对象）
        """
        # 检查标签是否已存在，避免唯一约束冲突
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            return TagResponse.from_orm(existing_tag)

        # 创建新标签
        db_tag = Tag(name=tag_data.name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)

        return TagResponse.from_orm(db_tag)
