from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.notification import NotificationType

class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    link: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool
