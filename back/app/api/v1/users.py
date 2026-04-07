# back/app/api/v1/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies import get_current_active_user
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def read_users_me(
        current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的详细信息

    需要在请求头中携带：Authorization: Bearer <token>
    """
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_user_me(
        update_data: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新当前用户的信息

    - **username**: 新用户名（可选）
    - **email**: 新邮箱（可选）
    - **password**: 新密码（可选）
    """
    return UserService.update_user(db, current_user, update_data)


@router.delete("/me", summary="删除当前用户账户")
async def delete_user_me(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    删除当前用户账户（软删除）
    """
    UserService.delete_user(db, current_user)
    return {"message": "User account deleted successfully"}