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
            tag_ids: Optional[List[int]] = None,
            title: Optional[str] = None
    ) -> BookmarkListResponse:
        """
        获取书签列表（支持分页、过滤和模糊搜索）

        Args:
            db: 数据库会话对象
            user_id: 当前用户ID，用于数据隔离
            page: 页码，默认为1
            page_size: 每页显示数量，默认为10
            category_id: 可选，按分类ID进行过滤
            tag_ids: 可选，按标签ID列表进行过滤（多对多关系）
            title: 可选，按标题进行模糊搜索（不区分大小写）

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
            # 使用子查询避免 JOIN 导致的重复记录
            # 找到包含任意一个指定标签的书签 ID
            from sqlalchemy import exists
            print(tag_ids)
            subquery = db.query(Bookmark.id).join(Bookmark.tags).filter(
                Tag.id.in_(tag_ids),
                Bookmark.user_id == user_id
            ).subquery()
            
            query = query.filter(Bookmark.id.in_(subquery))

        # 如果提供了标题搜索关键词，添加模糊搜索条件
        if title and title.strip():
            # MySQL 默认不区分大小写，直接使用 like 进行模糊匹配
            # PostgreSQL 用户可改用 ilike
            query = query.filter(Bookmark.title.like(f"%{title.strip()}%"))

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
            HTTPException: 如果 URL 匹配黑名单
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

        # 异步更新标签使用计数
        if bookmark_data.tag_ids:
            from app.services.tasks import update_tag_usage_task
            update_tag_usage_task.delay('create', {'tag_ids': bookmark_data.tag_ids})

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

        # 保存旧的标签ID列表
        old_tag_ids = [tag.id for tag in bookmark.tags]

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

        # 异步更新标签使用计数
        if tag_ids is not None:
            from app.services.tasks import update_tag_usage_task
            update_tag_usage_task.delay('update', {'old_tag_ids': old_tag_ids, 'new_tag_ids': tag_ids})

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
        
        # 保存标签ID列表（用于更新计数）
        tag_ids = [tag.id for tag in bookmark.tags]
        
        # 先删除关联的分享记录（避免外键约束错误）
        from app.models.bookmark_share import BookmarkShare
        db.query(BookmarkShare).filter(
            BookmarkShare.bookmark_id == bookmark_id
        ).delete(synchronize_session=False)
        
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


class StatisticsService:
    """统计服务类，提供数据分析和可视化所需的数据"""

    @staticmethod
    def get_user_overview(db: Session, user_id: int) -> dict:
        """
        获取用户数据概览
        
        Args:
            db: 数据库会话对象
            user_id: 用户ID
            
        Returns:
            dict: 包含书签总数、分类数、标签数、总点击数等统计信息
        """
        from sqlalchemy import func
        
        # 书签总数
        total_bookmarks = db.query(func.count(Bookmark.id)).filter(
            Bookmark.user_id == user_id
        ).scalar() or 0
        
        # 分类数量
        total_categories = db.query(func.count(Category.id)).filter(
            Category.user_id == user_id
        ).scalar() or 0
        
        # 用户使用的标签数量（去重）
        from app.models.bookmark import bookmark_tag
        total_tags = db.query(func.count(func.distinct(bookmark_tag.c.tag_id))).join(
            Bookmark, Bookmark.id == bookmark_tag.c.bookmark_id
        ).filter(
            Bookmark.user_id == user_id
        ).scalar() or 0
        
        # 总点击次数
        total_clicks = db.query(func.sum(Bookmark.click_count)).filter(
            Bookmark.user_id == user_id
        ).scalar() or 0
        
        # 本周新增书签数
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_this_week = db.query(func.count(Bookmark.id)).filter(
            Bookmark.user_id == user_id,
            Bookmark.created_at >= week_ago
        ).scalar() or 0
        
        return {
            "total_bookmarks": total_bookmarks,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "total_clicks": total_clicks,
            "new_this_week": new_this_week
        }

    @staticmethod
    def get_category_distribution(db: Session, user_id: int) -> List[dict]:
        """
        获取分类分布数据（用于饼图）
        
        Args:
            db: 数据库会话对象
            user_id: 用户ID
            
        Returns:
            List[dict]: 分类名称和数量的列表
        """
        from sqlalchemy import func
        
        # 查询每个分类的书签数量
        results = db.query(
            Category.name,
            func.count(Bookmark.id).label('count')
        ).join(
            Bookmark, Bookmark.category_id == Category.id
        ).filter(
            Category.user_id == user_id
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.count(Bookmark.id).desc()
        ).all()
        
        # 计算总数用于百分比
        total = sum(row.count for row in results)
        
        return [
            {
                "category_name": row.name,
                "count": row.count,
                "percentage": round((row.count / total * 100), 2) if total > 0 else 0
            }
            for row in results
        ]

    @staticmethod
    def get_top_bookmarks(db: Session, user_id: int, limit: int = 10) -> List[dict]:
        """
        获取热门书签（按点击次数排序）
        
        Args:
            db: 数据库会话对象
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            List[dict]: 热门书签列表
        """
        bookmarks = db.query(Bookmark).filter(
            Bookmark.user_id == user_id
        ).order_by(
            Bookmark.click_count.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": b.id,
                "title": b.title,
                "url": b.url,
                "click_count": b.click_count
            }
            for b in bookmarks
        ]

    @staticmethod
    def get_creation_trend(db: Session, user_id: int, days: int = 30) -> List[dict]:
        """
        获取书签创建趋势（最近N天）
        
        Args:
            db: 数据库会话对象
            user_id: 用户ID
            days: 天数
            
        Returns:
            List[dict]: 每日创建数量
        """
        from datetime import datetime, timedelta
        from sqlalchemy import func, cast, Date
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 查询每天的创建数量
        results = db.query(
            cast(Bookmark.created_at, Date).label('date'),
            func.count(Bookmark.id).label('count')
        ).filter(
            Bookmark.user_id == user_id,
            Bookmark.created_at >= start_date
        ).group_by(
            cast(Bookmark.created_at, Date)
        ).order_by(
            cast(Bookmark.created_at, Date)
        ).all()
        
        # 转换为字典列表
        trend_data = [
            {
                "date": row.date.strftime('%Y-%m-%d'),
                "count": row.count
            }
            for row in results
        ]
        
        # 补充缺失的日期（填充0）
        date_set = {item['date'] for item in trend_data}
        complete_data = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            if date in date_set:
                item = next(item for item in trend_data if item['date'] == date)
                complete_data.append(item)
            else:
                complete_data.append({"date": date, "count": 0})
        
        return complete_data

    @staticmethod
    def get_tag_usage_stats(db: Session, user_id: int, limit: int = 15) -> List[dict]:
        """
        获取标签使用统计（用于词云或柱状图）
        
        Args:
            db: 数据库会话对象
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            List[dict]: 标签使用次数统计
        """
        from app.models.bookmark import bookmark_tag
        from sqlalchemy import func
        
        results = db.query(
            Tag.name,
            func.count(bookmark_tag.c.bookmark_id).label('usage_count')
        ).join(
            bookmark_tag, Tag.id == bookmark_tag.c.tag_id
        ).join(
            Bookmark, Bookmark.id == bookmark_tag.c.bookmark_id
        ).filter(
            Bookmark.user_id == user_id
        ).group_by(
            Tag.id, Tag.name
        ).order_by(
            func.count(bookmark_tag.c.bookmark_id).desc()
        ).limit(limit).all()
        
        return [
            {
                "tag_name": row.name,
                "usage_count": row.usage_count
            }
            for row in results
        ]


class AdminTagService:
    """管理员标签服务类，提供标签的完整管理功能"""

    @staticmethod
    def get_all_tags_with_stats(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None
    ) -> dict:
        """
        获取所有标签及其使用统计（支持分页和分类筛选）

        Args:
            db: 数据库会话对象
            page: 页码，默认为1
            page_size: 每页数量，默认为20
            category_id: 可选，按分类ID过滤

        Returns:
            dict: 包含总记录数、当前页码、每页数量及标签列表的字典
        """
        query = db.query(Tag)
        
        if category_id is not None:
            query = query.filter(Tag.category_id == category_id)
        
        total = query.count()
        
        tags = query.order_by(Tag.usage_count.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [TagResponse.model_validate(t) for t in tags]
        }

    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> TagResponse:
        """
        管理员创建新标签

        Args:
            db: 数据库会话对象
            tag_data: 包含标签名称和分类ID的Pydantic模型

        Returns:
            TagResponse: 创建的标签响应对象

        Raises:
            HTTPException: 如果标签名称已存在或分类不存在
        """
        from fastapi import HTTPException, status

        # 检查标签是否已存在
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签 '{tag_data.name}' 已存在"
            )

        # 如果提供了分类ID，验证分类是否存在
        if tag_data.category_id:
            from app.models.tag_category import TagCategory
            category = db.query(TagCategory).filter(TagCategory.id == tag_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"标签分类 ID {tag_data.category_id} 不存在"
                )

        # 创建新标签
        db_tag = Tag(
            name=tag_data.name,
            category_id=tag_data.category_id,
            usage_count=0
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)

        return TagResponse.model_validate(db_tag)

    @staticmethod
    def update_tag(db: Session, tag_id: int, tag_name: str, category_id: Optional[int] = None) -> TagResponse:
        """
        管理员更新标签

        Args:
            db: 数据库会话对象
            tag_id: 标签ID
            tag_name: 新标签名称
            category_id: 新分类ID（可选，None表示不更新分类）

        Returns:
            TagResponse: 更新后的标签响应对象

        Raises:
            NotFoundError: 如果标签不存在
            HTTPException: 如果新名称与其他标签冲突或分类不存在
        """
        from fastapi import HTTPException, status

        # 获取标签
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise NotFoundError("标签不存在")

        # 检查新名称是否与其他标签冲突
        existing_tag = db.query(Tag).filter(
            Tag.name == tag_name,
            Tag.id != tag_id
        ).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签 '{tag_name}' 已存在"
            )

        # 如果提供了分类ID，验证分类是否存在
        if category_id is not None:
            from app.models.tag_category import TagCategory
            if category_id:  # 如果 category_id 不为 0 或 None
                category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"标签分类 ID {category_id} 不存在"
                    )
            tag.category_id = category_id

        # 更新标签名称
        tag.name = tag_name
        db.commit()
        db.refresh(tag)

        return TagResponse.model_validate(tag)

    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> bool:
        """
        管理员删除标签（严格模式：已使用的标签禁止删除）

        Args:
            db: 数据库会话对象
            tag_id: 标签ID

        Returns:
            bool: 删除成功返回True

        Raises:
            NotFoundError: 如果标签不存在
            HTTPException: 如果标签正在被使用
        """
        from fastapi import HTTPException, status

        # 获取标签
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise NotFoundError("标签不存在")

        # 检查标签是否被使用
        if tag.usage_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签 '{tag.name}' 正在被 {tag.usage_count} 个书签使用，无法删除"
            )

        # 删除标签
        db.delete(tag)
        db.commit()
        return True

    @staticmethod
    def update_tag_usage_count_on_bookmark_create(db: Session, tag_ids: List[int]):
        """
        创建书签时更新标签使用次数（增加）

        Args:
            db: 数据库会话对象
            tag_ids: 关联的标签ID列表
        """
        if not tag_ids:
            return

        db.query(Tag).filter(Tag.id.in_(tag_ids)).update(
            {Tag.usage_count: Tag.usage_count + 1},
            synchronize_session=False
        )
        db.commit()

    @staticmethod
    def update_tag_usage_count_on_bookmark_update(
            db: Session,
            old_tag_ids: List[int],
            new_tag_ids: List[int]
    ):
        """
        更新书签时更新标签使用次数（旧标签减1，新标签加1）

        Args:
            db: 数据库会话对象
            old_tag_ids: 更新前的标签ID列表
            new_tag_ids: 更新后的标签ID列表
        """
        old_set = set(old_tag_ids or [])
        new_set = set(new_tag_ids or [])

        # 需要减少计数的标签（在旧列表中但不在新列表中）
        to_decrease = old_set - new_set
        if to_decrease:
            db.query(Tag).filter(Tag.id.in_(to_decrease)).update(
                {Tag.usage_count: Tag.usage_count - 1},
                synchronize_session=False
            )

        # 需要增加计数的标签（在新列表中但不在旧列表中）
        to_increase = new_set - old_set
        if to_increase:
            db.query(Tag).filter(Tag.id.in_(to_increase)).update(
                {Tag.usage_count: Tag.usage_count + 1},
                synchronize_session=False
            )

        db.commit()

    @staticmethod
    def update_tag_usage_count_on_bookmark_delete(db: Session, tag_ids: List[int]):
        """
        删除书签时更新标签使用次数（减少）

        Args:
            db: 数据库会话对象
            tag_ids: 关联的标签ID列表
        """
        if not tag_ids:
            return

        db.query(Tag).filter(Tag.id.in_(tag_ids)).update(
            {Tag.usage_count: Tag.usage_count - 1},
            synchronize_session=False
        )
        db.commit()

