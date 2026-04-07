# back/app/models/user.py
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)  # 1: 激活, 0: 禁用

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"