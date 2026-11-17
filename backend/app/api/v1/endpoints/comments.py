from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.database.session import get_db
from app.models.user import User
from app.models.task import Task, TaskComment
from app.schemas.task import TaskCommentCreate, TaskCommentOut
from app.services.activity_service import log_activity, create_notification
from app.models.notification import NotificationType
from app.services.websocket_manager import manager

router = APIRouter()

@router.get("/task/{task_id}", response_model=List[TaskCommentOut])
def list_task_comments(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return db.query(TaskComment).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at.asc()).all()

@router.post("/task/{task_id}", response_model=TaskCommentOut)
async def create_task_comment(
    task_id: str,
    comment_in: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    log_activity(
        db,
        action="comment_added",
        details=f"Commented on '{task.title}': {comment.content[:60]}",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    # Notify task assignee if someone else comments
    if task.assignee_id and task.assignee_id != current_user.id:
        create_notification(
            db,
            user_id=task.assignee_id,
            title="New Comment on Task",
            message=f"{current_user.full_name} commented on '{task.title}'",
            notif_type=NotificationType.COMMENT_ADDED,
            link=f"/projects/{task.project_id}?task={task.id}"
        )

    # Broadcast WebSocket update
    await manager.broadcast(
        task.project_id,
        {
            "event": "COMMENT_ADDED",
            "task_id": task.id,
            "user": current_user.full_name,
            "content": comment.content
        }
    )

    return comment
