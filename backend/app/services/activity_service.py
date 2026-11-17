from typing import Optional
from sqlalchemy.orm import Session
from app.models.activity import ActivityLog
from app.models.notification import Notification, NotificationType

def log_activity(
    db: Session,
    action: str,
    details: Optional[str] = None,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None
) -> ActivityLog:
    activity = ActivityLog(
        action=action,
        details=details,
        user_id=user_id,
        project_id=project_id,
        task_id=task_id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notif_type: NotificationType,
    link: Optional[str] = None
) -> Notification:
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        link=link
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
