# back/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.db.database import init_db
from app.api.v1 import api_router


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例（工厂模式）"""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="云藏·智能收藏夹 API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 配置 CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()

upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup_event():
    """应用启动时执行"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


@app.get("/", tags=["根路径"])
def root():
    """根路径"""
    return {
        "message": "Welcome to 云藏·智能收藏夹 API",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )