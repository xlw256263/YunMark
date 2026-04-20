"""
创建官方分享快照表
执行方式: python migrations/create_official_share_snapshot_table.py
"""
from sqlalchemy import create_engine, text
from app.config import settings


def upgrade():
    """创建官方分享快照表"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # 创建表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS official_share_snapshots (
                id INT PRIMARY KEY AUTO_INCREMENT COMMENT '快照ID',
                share_id INT NOT NULL COMMENT '原始分享ID',
                bookmark_snapshot JSON NOT NULL COMMENT '书签数据快照',
                user_snapshot JSON COMMENT '用户信息快照（已脱敏）',
                curated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收录时间',
                curator_id INT COMMENT '运营人员ID',
                featured_level INT NOT NULL DEFAULT 0 COMMENT '推荐等级: 0-普通 1-精选 2-置顶',
                sort_weight INT NOT NULL DEFAULT 0 COMMENT '排序权重',
                is_visible TINYINT NOT NULL DEFAULT 1 COMMENT '是否可见: 0-隐藏 1-显示',
                takedown_reason TEXT COMMENT '下架原因',
                takedown_at DATETIME COMMENT '下架时间',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_share_id (share_id),
                INDEX idx_curated_at (curated_at),
                INDEX idx_featured_level (featured_level),
                INDEX idx_is_visible (is_visible),
                FOREIGN KEY (share_id) REFERENCES bookmark_shares(id) ON DELETE CASCADE,
                FOREIGN KEY (curator_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='官方分享快照表'
        """))

        conn.commit()
        print("✅ 官方分享快照表创建成功")


if __name__ == "__main__":
    upgrade()
