# back/app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.core.exceptions import ConflictError, NotFoundError


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
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

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
        # 检查邮箱是否已存在
        if UserService.get_user_by_email(db, user_data.email):
            raise ConflictError("该邮箱已被注册，请使用其他邮箱")

        # 检查用户名是否已存在
        if UserService.get_user_by_username(db, user_data.username):
            raise ConflictError("该用户名已被占用，请使用其他用户名")

        # 密码长度验证
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="密码长度至少为6位"
            )

        # 创建新用户
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

        # 如果更新密码，需要哈希
        if "password" in update_dict:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))

        for field, value in update_dict.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return UserResponse.from_orm(user)

    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """
        删除用户（软删除，设置为非激活状态）

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            bool 是否成功
        """
        user.is_active = 0
        db.commit()
        return True