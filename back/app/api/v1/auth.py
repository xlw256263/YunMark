# back/app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/token", response_model=TokenResponse, summary="用户登录获取Token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    OAuth2 标准登录端点

    - **username**: 用户邮箱
    - **password**: 用户密码

    返回 access_token 和用户信息
    """
    # 验证用户
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    # 创建 token
    return AuthService.create_token(user)


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """
    用户注册接口

    - **username**: 用户名
    - **email**: 邮箱
    - **password**: 密码

    返回注册成功的用户信息
    """
    return UserService.create_user(db, user_data)