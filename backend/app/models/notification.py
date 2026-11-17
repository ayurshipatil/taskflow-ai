import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.session import Base

class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    STATUS_CHANGED = "status_changed"
    DEADLINE_UPCOMING = "deadline_upcoming"
    OVERDUE = "overdue"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.TASK_ASSIGNED, nullable=False)
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
