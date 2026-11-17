from typing import Any, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.api import deps
from app.database.session import get_db
from app.models.user import User
from app.models.task import (
    Task, Subtask, TaskComment,
    TaskStatus, TaskPriority
)
from app.schemas.task import (
    TaskCreate, TaskOut, TaskDetailOut, TaskUpdate,
    SubtaskCreate, SubtaskOut
)
from app.services.activity_service import log_activity, create_notification
from app.models.notification import NotificationType
from app.services.websocket_manager import manager

router = APIRouter()

@router.get("", response_model=List[TaskOut])
def list_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    search: Optional[str] = None,
    my_tasks_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(Task)

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if my_tasks_only:
        query = query.filter(Task.assignee_id == current_user.id)
    elif assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(Task.title.ilike(search_filter), Task.description.ilike(search_filter))
        )

    tasks = query.order_by(Task.position.asc(), Task.created_at.desc()).all()

    # Populate subtasks and comments_count
    results = []
    for t in tasks:
        comm_count = db.query(func.count(TaskComment.id)).filter(TaskComment.task_id == t.id).scalar() or 0
        task_data = {
            "id": t.id,
            "project_id": t.project_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assignee_id": t.assignee_id,
            "start_date": t.start_date,
            "due_date": t.due_date,
            "estimated_hours": t.estimated_hours,
            "tags": t.tags,
            "position": t.position,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
            "assignee": t.assignee,
            "subtasks": t.subtasks,
            "comments_count": comm_count
        }
        results.append(task_data)
    return results

@router.post("", response_model=TaskOut)
async def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = Task(
        project_id=task_in.project_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status or TaskStatus.TODO,
        priority=task_in.priority or TaskPriority.MEDIUM,
        assignee_id=task_in.assignee_id,
        start_date=task_in.start_date,
        due_date=task_in.due_date,
        estimated_hours=task_in.estimated_hours or 0,
        tags=task_in.tags or "",
        position=task_in.position or 0
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    log_activity(
        db,
        action="task_created",
        details=f"Created task '{task.title}'",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    if task.assignee_id and task.assignee_id != current_user.id:
        create_notification(
            db,
            user_id=task.assignee_id,
            title="Task Assigned",
            message=f"{current_user.full_name} assigned you to '{task.title}'",
            notif_type=NotificationType.TASK_ASSIGNED,
            link=f"/projects/{task.project_id}?task={task.id}"
        )

    # Real-time WebSocket broadcast to project channel
    await manager.broadcast(
        task.project_id,
        {
            "event": "TASK_CREATED",
            "task_id": task.id,
            "title": task.title,
            "status": task.status.value,
            "user": current_user.full_name
        }
    )

    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assignee_id": task.assignee_id,
        "start_date": task.start_date,
        "due_date": task.due_date,
        "estimated_hours": task.estimated_hours,
        "tags": task.tags,
        "position": task.position,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assignee": task.assignee,
        "subtasks": [],
        "comments_count": 0
    }

@router.get("/{task_id}", response_model=TaskDetailOut)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comments = db.query(TaskComment).filter(TaskComment.task_id == task.id).order_by(TaskComment.created_at.asc()).all()

    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assignee_id": task.assignee_id,
        "start_date": task.start_date,
        "due_date": task.due_date,
        "estimated_hours": task.estimated_hours,
        "tags": task.tags,
        "position": task.position,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assignee": task.assignee,
        "subtasks": task.subtasks,
        "comments": comments,
        "comments_count": len(comments)
    }

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status
    old_assignee_id = task.assignee_id

    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)

    # Activity & Notification logic
    status_changed = (old_status != task.status)
    assignee_changed = (old_assignee_id != task.assignee_id)

    if status_changed:
        log_activity(
            db,
            action="status_updated",
            details=f"Moved task '{task.title}' to {task.status.value}",
            user_id=current_user.id,
            project_id=task.project_id,
            task_id=task.id
        )
        if task.assignee_id and task.assignee_id != current_user.id:
            create_notification(
                db,
                user_id=task.assignee_id,
                title="Task Status Changed",
                message=f"{current_user.full_name} moved '{task.title}' to {task.status.value}",
                notif_type=NotificationType.STATUS_CHANGED,
                link=f"/projects/{task.project_id}?task={task.id}"
            )

    if assignee_changed and task.assignee_id:
        log_activity(
            db,
            action="task_reassigned",
            details=f"Reassigned '{task.title}'",
            user_id=current_user.id,
            project_id=task.project_id,
            task_id=task.id
        )
        if task.assignee_id != current_user.id:
            create_notification(
                db,
                user_id=task.assignee_id,
                title="Task Assigned",
                message=f"{current_user.full_name} assigned you to '{task.title}'",
                notif_type=NotificationType.TASK_ASSIGNED,
                link=f"/projects/{task.project_id}?task={task.id}"
            )

    # Broadcast WebSocket update
    await manager.broadcast(
        task.project_id,
        {
            "event": "TASK_UPDATED",
            "task_id": task.id,
            "status": task.status.value,
            "priority": task.priority.value,
            "user": current_user.full_name
        }
    )

    comm_count = db.query(func.count(TaskComment.id)).filter(TaskComment.task_id == task.id).scalar() or 0

    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assignee_id": task.assignee_id,
        "start_date": task.start_date,
        "due_date": task.due_date,
        "estimated_hours": task.estimated_hours,
        "tags": task.tags,
        "position": task.position,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assignee": task.assignee,
        "subtasks": task.subtasks,
        "comments_count": comm_count
    }

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project_id = task.project_id
    title = task.title
    db.delete(task)
    db.commit()

    log_activity(
        db,
        action="task_deleted",
        details=f"Deleted task '{title}'",
        user_id=current_user.id,
        project_id=project_id
    )

    await manager.broadcast(
        project_id,
        {
            "event": "TASK_DELETED",
            "task_id": task_id,
            "title": title,
            "user": current_user.full_name
        }
    )

    return {"message": f"Task '{title}' deleted successfully"}

# Subtasks
@router.post("/{task_id}/subtasks", response_model=SubtaskOut)
def create_subtask(
    task_id: str,
    subtask_in: SubtaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    subtask = Subtask(
        task_id=task_id,
        title=subtask_in.title,
        is_completed=False
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask

@router.patch("/subtasks/{subtask_id}", response_model=SubtaskOut)
def toggle_subtask(
    subtask_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    subtask.is_completed = not subtask.is_completed
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask

@router.delete("/subtasks/{subtask_id}")
def delete_subtask(
    subtask_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"message": "Subtask deleted"}
