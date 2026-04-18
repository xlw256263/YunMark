# back/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


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


class UserProfileUpdate(BaseModel):
    """更新个人资料请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class PasswordChange(BaseModel):
    """修改密码请求模型"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    """用户响应模型（不包含密码）"""
    id: int
    is_active: int
    role: str = 'user'
    avatar: Optional[str] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": 1,
                "role": "user",
                "avatar": "https://example.com/avatar.jpg",
                "bio": "这是我的个人简介",
                "created_at": "2024-01-01T00:00:00"
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


class AvatarUploadResponse(BaseModel):
    """头像上传响应模型"""
    avatar_url: str
    message: str = "头像上传成功"
