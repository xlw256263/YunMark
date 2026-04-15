# back/app/services/auth_service.py
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import TokenResponse
from app.config import settings
from fastapi import HTTPException, status


class AuthService:
    """认证服务"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        验证用户凭证

        Args:
            db: 数据库会话
            email: 用户邮箱
            password: 明文密码

        Returns:
            User 对象

        Raises:
            HTTPException: 如果用户不存在、密码错误或账号已禁用
        """
        # 查询用户
        user = db.query(User).filter(User.email == email).first()

        # 用户不存在
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱未注册，请先注册账号",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 密码错误
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误，请重新输入",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 账号已禁用
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用，请联系管理员",
            )

        return user

    @staticmethod
    def create_token(user: User) -> TokenResponse:
        """
        为用户创建访问令牌

        Args:
            user: 用户对象

        Returns:
            TokenResponse 包含 access_token 和用户信息
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            username=user.username,
            email=user.email
        )