from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.tag_category import TagCategory
from app.schemas.tag_category import (
    TagCategoryCreate,
    TagCategoryUpdate,
    TagCategoryResponse
)
from app.core.exceptions import NotFoundError


class TagCategoryService:
    """标签分类服务类"""

    @staticmethod
    def get_all_categories(db: Session, sort_by_order: bool = True) -> List[TagCategoryResponse]:
        """
        获取所有标签分类（按排序顺序）
        """
        query = db.query(TagCategory)
        if sort_by_order:
            query = query.order_by(TagCategory.sort_order.asc(), TagCategory.id.asc())
        categories = query.all()
        return [TagCategoryResponse.model_validate(c) for c in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> TagCategory:
        """
        根据 ID 获取标签分类
        """
        category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
        if not category:
            raise NotFoundError("标签分类不存在")
        return category

    @staticmethod
    def create_category(db: Session, category_data: TagCategoryCreate) -> TagCategoryResponse:
        """
        创建标签分类
        """
        from fastapi import HTTPException, status

        # 检查名称是否已存在
        existing = db.query(TagCategory).filter(TagCategory.name == category_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签分类 '{category_data.name}' 已存在"
            )

        db_category = TagCategory(
            name=category_data.name,
            description=category_data.description,
            sort_order=category_data.sort_order
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)

        return TagCategoryResponse.model_validate(db_category)

    @staticmethod
    def update_category(
            db: Session,
            category_id: int,
            update_data: TagCategoryUpdate
    ) -> TagCategoryResponse:
        """
        更新标签分类
        """
        from fastapi import HTTPException, status

        category = TagCategoryService.get_category_by_id(db, category_id)

        update_dict = update_data.model_dump(exclude_unset=True)

        # 如果更新名称，检查是否与其他分类冲突
        if "name" in update_dict:
            existing = db.query(TagCategory).filter(
                TagCategory.name == update_dict["name"],
                TagCategory.id != category_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"标签分类 '{update_dict['name']}' 已存在"
                )

        for field, value in update_dict.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)

        return TagCategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """
        删除标签分类（严格模式：有标签的分类禁止删除）
        """
        from fastapi import HTTPException, status

        category = TagCategoryService.get_category_by_id(db, category_id)

        # 检查是否有标签使用此分类
        if category.tags:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签分类 '{category.name}' 下有 {len(category.tags)} 个标签，无法删除"
            )

        db.delete(category)
        db.commit()
        return True

