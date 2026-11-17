from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskPriority
from app.schemas.user import UserOut

class SubtaskBase(BaseModel):
    title: str

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskOut(SubtaskBase):
    id: str
    task_id: str
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCommentCreate(BaseModel):
    content: str

class TaskCommentOut(BaseModel):
    id: str
    task_id: str
    user_id: str
    content: str
    created_at: datetime
    author: Optional[UserOut] = None

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = 0
    tags: Optional[str] = ""
    position: Optional[int] = 0

class TaskCreate(TaskBase):
    project_id: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    position: Optional[int] = None

class TaskOut(TaskBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserOut] = None
    subtasks: List[SubtaskOut] = []
    comments_count: Optional[int] = 0

    class Config:
        from_attributes = True

class TaskDetailOut(TaskOut):
    comments: List[TaskCommentOut] = []
