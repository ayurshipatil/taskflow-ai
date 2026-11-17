from typing import Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.database.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.analytics import (
    DashboardMetrics, StatusCount, PriorityCount,
    MemberWorkload, TaskCompletionTrend
)

router = APIRouter()

@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project_query = db.query(Project)
    task_query = db.query(Task)

    if workspace_id:
        project_query = project_query.filter(Project.workspace_id == workspace_id)
        # Filter tasks by projects in this workspace
        subq = db.query(Project.id).filter(Project.workspace_id == workspace_id).subquery()
        task_query = task_query.filter(Task.project_id.in_(subq))

    if project_id:
        task_query = task_query.filter(Task.project_id == project_id)

    total_projects = project_query.count()
    total_tasks = task_query.count()
    completed_tasks = task_query.filter(Task.status == TaskStatus.COMPLETED).count()
    pending_tasks = total_tasks - completed_tasks

    today = date.today()
    overdue_tasks = task_query.filter(
        Task.status != TaskStatus.COMPLETED,
        Task.due_date < today
    ).count()

    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    # Status distribution
    status_counts_raw = (
        task_query.with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
    status_map = {s.value: 0 for s in TaskStatus}
    for st, count in status_counts_raw:
        status_map[st.value] = count
    status_distribution = [StatusCount(status=k, count=v) for k, v in status_map.items()]

    # Priority distribution
    priority_counts_raw = (
        task_query.with_entities(Task.priority, func.count(Task.id))
        .group_by(Task.priority)
        .all()
    )
    priority_map = {p.value: 0 for p in TaskPriority}
    for pr, count in priority_counts_raw:
        priority_map[pr.value] = count
    priority_distribution = [PriorityCount(priority=k, count=v) for k, v in priority_map.items()]

    # Team Workload distribution
    users = db.query(User).filter(User.is_active == True).all()
    workload = []
    for u in users:
        assigned = task_query.filter(Task.assignee_id == u.id).count()
        completed = task_query.filter(Task.assignee_id == u.id, Task.status == TaskStatus.COMPLETED).count()
        if assigned > 0 or completed > 0:
            workload.append(MemberWorkload(
                user_id=u.id,
                name=u.full_name,
                assigned_count=assigned,
                completed_count=completed
            ))

    # Task completion trend (last 7 days from actual records)
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%b %d")
        
        # Count tasks created on this day
        start_dt = datetime.combine(day, datetime.min.time())
        end_dt = datetime.combine(day, datetime.max.time())
        created_cnt = task_query.filter(Task.created_at >= start_dt, Task.created_at <= end_dt).count()
        
        # Completed on this day (via updated_at)
        completed_cnt = task_query.filter(
            Task.status == TaskStatus.COMPLETED,
            Task.updated_at >= start_dt,
            Task.updated_at <= end_dt
        ).count()

        trend.append(TaskCompletionTrend(
            date=day_str,
            completed=completed_cnt,
            created=created_cnt
        ))

    return DashboardMetrics(
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=completion_rate,
        status_distribution=status_distribution,
        priority_distribution=priority_distribution,
        workload=workload,
        completion_trend=trend
    )
