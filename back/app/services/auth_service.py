# back/app/services/auth_service.py
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import TokenResponse
from app.config import settings


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
            ValueError: 如果用户不存在或密码错误
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise ValueError("Incorrect email or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Incorrect email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

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
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            username=user.username,
            email=user.email
        )