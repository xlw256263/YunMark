# back/app/dependencies.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.config import settings
from app.core.exceptions import AuthenticationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户

    Args:
        token: JWT token
        db: 数据库会话

    Returns:
        User 对象

    Raises:
        AuthenticationError: 如果 token 无效或用户不存在
    """
    credentials_exception = AuthenticationError()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活的用户

    Args:
        current_user: 当前用户对象

    Returns:
        User 对象
    """
    return current_user


def get_current_admin_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户（权限依赖）

    Args:
        current_user: 当前用户对象

    Returns:
        User 对象（必须是 admin 角色）

    Raises:
        AuthenticationError: 如果用户不是管理员
    """
    if current_user.role != 'admin':
        raise AuthenticationError("需要管理员权限")
    
    return current_user
