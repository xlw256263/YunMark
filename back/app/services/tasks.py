from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.services.bookmark_service import AdminTagService

@celery_app.task
def update_tag_usage_task(action: str, data: dict):
    """
    异步更新标签使用计数的 Celery 任务
    action: 'create' | 'update' | 'delete'
    data: 任务所需的参数
    """
    db = SessionLocal()
    try:
        if action == 'create':
            AdminTagService.update_tag_usage_count_on_bookmark_create(db, data['tag_ids'])
        elif action == 'update':
            AdminTagService.update_tag_usage_count_on_bookmark_update(db, data['old_tag_ids'], data['new_tag_ids'])
        elif action == 'delete':
            AdminTagService.update_tag_usage_count_on_bookmark_delete(db, data['tag_ids'])
    finally:
        db.close()
