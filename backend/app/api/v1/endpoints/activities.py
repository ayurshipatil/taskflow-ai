from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.database.session import get_db
from app.models.user import User
from app.models.activity import ActivityLog
from app.schemas.activity import ActivityLogOut

router = APIRouter()

@router.get("", response_model=List[ActivityLogOut])
def get_activities(
    project_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(ActivityLog)
    if project_id:
        query = query.filter(ActivityLog.project_id == project_id)
    return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
