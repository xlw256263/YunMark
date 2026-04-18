# back/app/api/v1/users.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserProfileUpdate, PasswordChange, AvatarUploadResponse
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


@router.patch("/me/profile", response_model=UserResponse, summary="更新个人资料")
async def update_profile(
        profile_data: UserProfileUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    更新用户个人资料

    - **username**: 新用户名（可选，2-50字符）
    - **email**: 新邮箱（可选）
    - **avatar**: 头像URL（可选）
    - **bio**: 个人简介（可选，最多500字符）
    """
    return UserService.update_profile(db, current_user, profile_data)


@router.post("/me/change-password", summary="修改密码")
async def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    修改用户密码

    - **old_password**: 原密码
    - **new_password**: 新密码（6-100字符）
    """
    return UserService.change_password(db, current_user, password_data)


@router.post("/me/avatar", response_model=AvatarUploadResponse, summary="上传头像")
async def upload_avatar(
        file: UploadFile = File(..., description="头像文件（JPG/PNG/GIF/WEBP，最大5MB）"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    上传用户头像

    支持格式：JPG、PNG、GIF、WEBP
    文件大小限制：5MB
    """
    avatar_url = await UserService.upload_avatar(current_user, file)
    
    current_user.avatar = avatar_url
    db.commit()
    
    return AvatarUploadResponse(avatar_url=avatar_url)


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