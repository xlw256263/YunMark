"""
数据库迁移脚本：创建书签分享表 bookmark_shares

使用方法：
cd back
python migrations/add_bookmark_share_table.py
"""
from sqlalchemy import create_engine, text
from app.config import settings
import sys


def create_bookmark_share_table():
    """创建书签分享表"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # 检查表是否已存在
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'bookmark_shares'
            """))
            
            if result.fetchone():
                print("○ bookmark_shares 表已存在，跳过创建")
                conn.commit()
                return
            
            print("创建 bookmark_shares 表...")
            conn.execute(text("""
                CREATE TABLE bookmark_shares (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分享记录ID',
                    bookmark_id INT NOT NULL COMMENT '书签ID',
                    user_id INT NOT NULL COMMENT '分享用户ID',
                    status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '分享状态',
                    review_note TEXT NULL COMMENT '审核备注',
                    reject_reason TEXT NULL COMMENT '驳回原因',
                    submitted_at DATETIME NULL COMMENT '提交审核时间',
                    reviewed_at DATETIME NULL COMMENT '审核时间',
                    reviewer_id INT NULL COMMENT '审核人ID',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    
                    INDEX idx_bookmark_id (bookmark_id),
                    INDEX idx_user_id (user_id),
                    INDEX idx_status (status),
                    INDEX idx_reviewer_id (reviewer_id),
                    
                    FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='书签分享记录表'
            """))
            
            conn.commit()
            print("✓ bookmark_shares 表创建成功")
            print("\n✅ 数据库迁移完成！")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ 迁移失败: {str(e)}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    print("开始执行数据库迁移...\n")
    create_bookmark_share_table()
