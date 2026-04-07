# back/app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.base_class import Base

# 创建数据库引擎，配置连接池参数以优化性能和稳定性
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 在每次 checkout 时检查连接是否有效
    pool_recycle=3600,   # 连接在池中保留的最大时间（秒），防止连接过期
)

# 创建数据库会话工厂，配置自动提交和自动刷新行为
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)