from typing import Any, List
from datetime import date, timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.database.session import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task, Subtask, TaskStatus, TaskPriority
from app.schemas.ai import (
    TaskGeneratorRequest, GeneratedTaskResponse,
    ProjectBreakdownRequest, ProjectBreakdownResponse,
    ProjectHealthResponse, AIChatRequest, AIChatResponse,
    ProjectPhase
)
from app.services.ai_service import ai_service
from app.services.activity_service import log_activity

router = APIRouter()

class ImportBreakdownRequest(BaseModel):
    project_id: str
    phases: List[ProjectPhase]

@router.post("/generate-tasks", response_model=GeneratedTaskResponse)
async def generate_task(
    request: TaskGeneratorRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return await ai_service.generate_task(request.requirement)

@router.post("/project-breakdown", response_model=ProjectBreakdownResponse)
async def breakdown_project(
    request: ProjectBreakdownRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return await ai_service.breakdown_project(request.project_idea)

@router.post("/import-breakdown")
def import_breakdown(
    req: ImportBreakdownRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    created_tasks_count = 0
    today = date.today()

    for phase in req.phases:
        for t in phase.tasks:
            due_d = today + timedelta(days=t.suggested_days_from_start)
            db_task = Task(
                project_id=project.id,
                title=f"[{phase.phase_name.split(':')[0].strip()}] {t.title}",
                description=t.description,
                priority=t.priority,
                status=TaskStatus.TODO,
                assignee_id=current_user.id,
                due_date=due_d,
                estimated_hours=t.estimated_hours,
                tags=phase.phase_name.split(':')[0].strip().lower()
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            created_tasks_count += 1

            # Subtasks
            for sub_title in t.subtasks:
                sub = Subtask(
                    task_id=db_task.id,
                    title=sub_title,
                    is_completed=False
                )
                db.add(sub)
            db.commit()

    log_activity(
        db,
        action="ai_plan_imported",
        details=f"Imported {created_tasks_count} tasks from AI Project Breakdown into '{project.name}'",
        user_id=current_user.id,
        project_id=project.id
    )

    return {
        "message": f"Successfully created {created_tasks_count} tasks in project '{project.name}'",
        "created_count": created_tasks_count
    }

@router.get("/project-health/{project_id}", response_model=ProjectHealthResponse)
def get_project_health(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    pending_tasks = total_tasks - completed_tasks

    today = date.today()
    overdue_tasks = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED and t.due_date and t.due_date < today)
    high_priority_pending = sum(
        1 for t in tasks if t.status != TaskStatus.COMPLETED and t.priority in (TaskPriority.HIGH, TaskPriority.CRITICAL)
    )
    unassigned_tasks = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED and not t.assignee_id)
    member_count = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).count()

    return ai_service.analyze_project_health(
        project_name=project.name,
        project_id=project.id,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        high_priority_pending=high_priority_pending,
        member_count=member_count,
        unassigned_tasks=unassigned_tasks
    )

@router.post("/assistant-chat", response_model=AIChatResponse)
async def chat_assistant(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project_context = None
    if request.project_id:
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if project:
            tasks = db.query(Task).filter(Task.project_id == project.id).all()
            today = date.today()
            project_context = {
                "name": project.name,
                "status": project.status.value,
                "total_tasks": len(tasks),
                "completed_tasks": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
                "pending_tasks": sum(1 for t in tasks if t.status != TaskStatus.COMPLETED),
                "overdue_tasks": sum(1 for t in tasks if t.status != TaskStatus.COMPLETED and t.due_date and t.due_date < today),
                "my_tasks_count": sum(1 for t in tasks if t.assignee_id == current_user.id)
            }

    return await ai_service.chat_assistant(
        user_message=request.message,
        user_name=current_user.full_name,
        project_context=project_context
    )
