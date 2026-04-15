# back/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1 import auth, users, bookmarks

api_router = APIRouter()

# 注册路由
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(bookmarks.router)