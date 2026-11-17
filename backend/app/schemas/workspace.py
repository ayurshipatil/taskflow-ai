from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.workspace import WorkspaceRole
from app.schemas.user import UserOut

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    slug: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WorkspaceMemberAdd(BaseModel):
    email: str
    role: WorkspaceRole = WorkspaceRole.MEMBER

class WorkspaceMemberOut(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: WorkspaceRole
    joined_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class WorkspaceOut(WorkspaceBase):
    id: str
    slug: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True
