from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.dependencies import get_current_active_user
from app.services.bookmark_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["数据统计"])


@router.get("/overview", summary="获取数据概览")
async def get_statistics_overview(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的数据概览

    返回：
    - 书签总数
    - 分类数量
    - 标签数量
    - 总点击次数
    - 本周新增数量
    """
    return StatisticsService.get_user_overview(db, current_user.id)


@router.get("/category-distribution", response_model=List[dict], summary="获取分类分布")
async def get_category_distribution(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取分类分布数据（用于饼图展示）

    返回每个分类的书签数量和占比
    """
    return StatisticsService.get_category_distribution(db, current_user.id)


@router.get("/top-bookmarks", response_model=List[dict], summary="获取热门书签")
async def get_top_bookmarks(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取点击次数最多的热门书签
    """
    return StatisticsService.get_top_bookmarks(db, current_user.id, limit)


@router.get("/creation-trend", response_model=List[dict], summary="获取创建趋势")
async def get_creation_trend(
        days: int = Query(30, ge=7, le=90, description="天数范围"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取书签创建趋势（最近N天）

    默认返回最近30天的数据
    """
    return StatisticsService.get_creation_trend(db, current_user.id, days)


@router.get("/tag-usage", response_model=List[dict], summary="获取标签使用统计")
async def get_tag_usage_stats(
        limit: int = Query(15, ge=5, le=30, description="返回数量"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取标签使用频率统计
    """
    return StatisticsService.get_tag_usage_stats(db, current_user.id, limit)
