from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectPriority
from app.schemas.user import UserOut

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.PLANNING
    priority: Optional[ProjectPriority] = ProjectPriority.MEDIUM
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    manager_id: Optional[str] = None

class ProjectCreate(ProjectBase):
    workspace_id: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    manager_id: Optional[str] = None

class ProjectMemberAdd(BaseModel):
    user_id: str
    role: Optional[str] = "member"

class ProjectMemberOut(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: str
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class ProjectOut(ProjectBase):
    id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    manager: Optional[UserOut] = None
    task_count: Optional[int] = 0
    completed_task_count: Optional[int] = 0
    progress_percentage: Optional[float] = 0.0

    class Config:
        from_attributes = True
