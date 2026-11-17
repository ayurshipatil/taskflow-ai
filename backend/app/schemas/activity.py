from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserOut

class ActivityLogOut(BaseModel):
    id: str
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    action: str
    details: Optional[str] = None
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
