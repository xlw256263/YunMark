# back/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1 import auth, users, bookmarks, admin, statistics, shares, admin_shares, public_shares, admin_blacklist

api_router = APIRouter()

# 注册路由
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(bookmarks.router)
api_router.include_router(admin.router)
api_router.include_router(statistics.router)
api_router.include_router(shares.router)
api_router.include_router(admin_shares.router)
api_router.include_router(public_shares.router)
api_router.include_router(admin_blacklist.router, prefix="/admin/blacklist", tags=["admin-blacklist"])
