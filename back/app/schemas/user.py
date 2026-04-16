# back/app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: str


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型（不包含密码）"""
    id: int
    is_active: int
    role: str = 'user'

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": 1,
                "role": "user"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: str
    password: str


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token 数据模型（用于解码后的数据）"""
    username: Optional[str] = None


class TokenResponse(Token):
    """扩展的 Token 响应（包含完整用户信息）"""
    user: UserResponse
