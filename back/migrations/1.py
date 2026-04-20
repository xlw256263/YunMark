"""
将历史已通过的分享数据迁移到官方快照表
执行方式: python migrations/migrate_approved_shares_to_snapshots.py
"""
from sqlalchemy import create_engine, text
from datetime import datetime
import json
from app.config import settings


def migrate():
    """迁移已通过的分享数据到快照表"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # 查询所有已通过的分享记录
        result = conn.execute(text("""
            SELECT 
                bs.id as share_id,
                bs.bookmark_id,
                bs.user_id,
                bs.reviewed_at,
                bs.reviewer_id,
                b.title,
                b.url,
                b.description,
                b.favicon,
                b.click_count,
                u.username,
                u.avatar
            FROM bookmark_shares bs
            JOIN bookmarks b ON bs.bookmark_id = b.id
            LEFT JOIN users u ON bs.user_id = u.id
            WHERE bs.status = 'approved'
              AND bs.id NOT IN (SELECT share_id FROM official_share_snapshots)
        """))

        rows = result.fetchall()

        if not rows:
            print("✅ 没有需要迁移的数据")
            return

        print(f"📦 发现 {len(rows)} 条需要迁移的数据")

        # 插入快照表
        migrated_count = 0
        for row in rows:
            share_id, bookmark_id, user_id, reviewed_at, reviewer_id, \
            title, url, description, favicon, click_count, username, avatar = row

            # 构建书签快照
            bookmark_snapshot = {
                "id": bookmark_id,
                "title": title,
                "url": url,
                "description": description,
                "favicon": favicon,
                "click_count": click_count or 0
            }

            # 构建用户快照（脱敏）
            user_snapshot = None
            if username:
                user_snapshot = {
                    "username": username,
                    "avatar_url": avatar
                }

            # 插入快照记录
            conn.execute(text("""
                INSERT INTO official_share_snapshots 
                (share_id, bookmark_snapshot, user_snapshot, curated_at, curator_id, 
                 featured_level, sort_weight, is_visible)
                VALUES 
                (:share_id, :bookmark_snapshot, :user_snapshot, :curated_at, :curator_id,
                 0, 0, 1)
            """), {
                "share_id": share_id,
                "bookmark_snapshot": json.dumps(bookmark_snapshot, ensure_ascii=False),
                "user_snapshot": json.dumps(user_snapshot, ensure_ascii=False) if user_snapshot else None,
                "curated_at": reviewed_at or datetime.utcnow(),
                "curator_id": reviewer_id
            })

            migrated_count += 1

        conn.commit()
        print(f"✅ 成功迁移 {migrated_count} 条数据到官方快照表")


if __name__ == "__main__":
    migrate()
