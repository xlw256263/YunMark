# back/app/config.py
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Settings:
    """应用配置类"""

    # 应用基本信息
    APP_NAME: str = "云藏·智能收藏夹"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/user?charset=utf8"  # 默认值
    )

    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
