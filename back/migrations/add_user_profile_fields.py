"""
数据库迁移脚本：为 users 表添加头像、简介和创建时间字段

使用方法：
cd back
python migrations/add_user_profile_fields.py
"""
from sqlalchemy import create_engine, text
from app.config import settings
import sys


def add_user_profile_fields():
    """添加用户资料相关字段"""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'users'
            """))

            existing_columns = [row[0] for row in result.fetchall()]

            # 添加 avatar 字段
            if 'avatar' not in existing_columns:
                print("添加 avatar 字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN avatar VARCHAR(500) NULL COMMENT '头像URL'
                """))
                print("✓ avatar 字段添加成功")
            else:
                print("○ avatar 字段已存在，跳过")

            # 添加 bio 字段
            if 'bio' not in existing_columns:
                print("添加 bio 字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN bio TEXT NULL COMMENT '个人简介'
                """))
                print("✓ bio 字段添加成功")
            else:
                print("○ bio 字段已存在，跳过")

            # 添加 created_at 字段
            if 'created_at' not in existing_columns:
                print("添加 created_at 字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
                """))

                # 为现有用户设置默认创建时间
                conn.execute(text("""
                    UPDATE users 
                    SET created_at = NOW() 
                    WHERE created_at IS NULL
                """))
                print("✓ created_at 字段添加成功")
            else:
                print("○ created_at 字段已存在，跳过")

            conn.commit()
            print("\n✅ 数据库迁移完成！")

        except Exception as e:
            conn.rollback()
            print(f"\n❌ 迁移失败: {str(e)}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    print("开始执行数据库迁移...\n")
    add_user_profile_fields()
