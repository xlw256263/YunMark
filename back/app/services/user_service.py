# back/app/services/user_service.py
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfileUpdate, PasswordChange
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import ConflictError, NotFoundError
from app.config import settings


class UserService:
    """用户服务"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """根据 ID 获取用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """根据邮箱获取用户（只查询激活状态的用户）"""
        return db.query(User).filter(User.email == email, User.is_active == 1).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户（只查询激活状态的用户）"""
        return db.query(User).filter(User.username == username, User.is_active == 1).first()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        """
        创建新用户

        Args:
            db: 数据库会话
            user_data: 用户创建数据

        Returns:
            UserResponse 用户响应对象

        Raises:
            ConflictError: 如果邮箱或用户名已存在
        """
        if UserService.get_user_by_email(db, user_data.email):
            raise ConflictError("该邮箱已被注册，请使用其他邮箱")

        if UserService.get_user_by_username(db, user_data.username):
            raise ConflictError("该用户名已被占用，请使用其他用户名")

        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="密码长度至少为6位"
            )

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=1
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return UserResponse.from_orm(db_user)

    @staticmethod
    def update_user(db: Session, user: User, update_data: UserUpdate) -> UserResponse:
        """
        更新用户信息

        Args:
            db: 数据库会话
            user: 用户对象
            update_data: 更新数据

        Returns:
            UserResponse 更新后的用户对象
        """
        update_dict = update_data.dict(exclude_unset=True)

        if "password" in update_dict:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))

        for field, value in update_dict.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return UserResponse.from_orm(user)

    @staticmethod
    def update_profile(db: Session, user: User, profile_data: UserProfileUpdate) -> UserResponse:
        """
        更新用户个人资料

        Args:
            db: 数据库会话
            user: 用户对象
            profile_data: 个人资料更新数据

        Returns:
            UserResponse 更新后的用户对象
        """
        if profile_data.username:
            existing_user = UserService.get_user_by_username(db, profile_data.username)
            if existing_user and existing_user.id != user.id:
                raise ConflictError("该用户名已被占用")
            user.username = profile_data.username

        if profile_data.email:
            existing_user = UserService.get_user_by_email(db, profile_data.email)
            if existing_user and existing_user.id != user.id:
                raise ConflictError("该邮箱已被使用")
            user.email = profile_data.email

        if profile_data.avatar is not None:
            user.avatar = profile_data.avatar

        if profile_data.bio is not None:
            user.bio = profile_data.bio

        db.commit()
        db.refresh(user)

        return UserResponse.from_orm(user)

    @staticmethod
    def change_password(db: Session, user: User, password_data: PasswordChange) -> dict:
        """
        修改密码

        Args:
            db: 数据库会话
            user: 用户对象
            password_data: 密码修改数据

        Returns:
            dict 操作结果
        """
        if not verify_password(password_data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )

        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="新密码长度至少为6位"
            )

        user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()

        return {"message": "密码修改成功"}

    @staticmethod
    async def upload_avatar(user: User, file: UploadFile) -> str:
        """
        上传头像

        Args:
            user: 用户对象
            file: 上传的文件

        Returns:
            str 头像URL
        """
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持 JPG、PNG、GIF、WEBP 格式的图片"
            )

        max_size = 5 * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片大小不能超过 5MB"
            )

        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{user.id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(contents)

        avatar_url = f"/uploads/avatars/{unique_filename}"
        return avatar_url

    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """
        删除用户（软删除，设置为非激活状态）
        同时修改用户名和邮箱，解除数据库唯一性约束

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            bool 是否成功
        """
        import time
        
        user.is_active = 0

        timestamp = int(time.time())
        user.username = f"{user.username}_deleted_{timestamp}"
        user.email = f"{user.email}_deleted_{timestamp}"

        db.commit()
        return True