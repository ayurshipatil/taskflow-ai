from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectStatus
from app.models.task import Task, TaskStatus
from app.schemas.project import (
    ProjectCreate, ProjectOut, ProjectUpdate,
    ProjectMemberAdd, ProjectMemberOut
)
from app.services.activity_service import log_activity

router = APIRouter()

def compute_project_stats(project: Project, db: Session) -> dict:
    total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project.id,
        Task.status == TaskStatus.COMPLETED
    ).scalar() or 0
    progress = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    return {
        "task_count": total_tasks,
        "completed_task_count": completed_tasks,
        "progress_percentage": progress
    }

@router.get("", response_model=List[ProjectOut])
def list_projects(
    workspace_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(Project)
    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)
    if status_filter:
        query = query.filter(Project.status == status_filter)

    projects = query.all()
    results = []
    for p in projects:
        stats = compute_project_stats(p, db)
        p_dict = {
            "id": p.id,
            "workspace_id": p.workspace_id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "priority": p.priority,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "manager_id": p.manager_id,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "manager": p.manager,
            "task_count": stats["task_count"],
            "completed_task_count": stats["completed_task_count"],
            "progress_percentage": stats["progress_percentage"]
        }
        results.append(p_dict)
    return results

@router.post("", response_model=ProjectOut)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = Project(
        workspace_id=project_in.workspace_id,
        name=project_in.name,
        description=project_in.description,
        status=project_in.status or ProjectStatus.PLANNING,
        priority=project_in.priority,
        start_date=project_in.start_date,
        end_date=project_in.end_date,
        manager_id=project_in.manager_id or current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Automatically add creator as a project member
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="lead"
    )
    db.add(member)
    db.commit()

    log_activity(
        db,
        action="project_created",
        details=f"Created project '{project.name}'",
        user_id=current_user.id,
        project_id=project.id
    )

    stats = compute_project_stats(project, db)
    return {
        **project.__dict__,
        "manager": project.manager,
        **stats
    }

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = compute_project_stats(project, db)
    return {
        **project.__dict__,
        "manager": project.manager,
        **stats
    }

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Enforce role-based permission
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and project.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only Admins or Project Managers can modify this project.")

    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.add(project)
    db.commit()
    db.refresh(project)

    log_activity(
        db,
        action="project_updated",
        details=f"Updated details for project '{project.name}'",
        user_id=current_user.id,
        project_id=project.id
    )

    stats = compute_project_stats(project, db)
    return {
        **project.__dict__,
        "manager": project.manager,
        **stats
    }

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and project.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only Admins or Project Managers can delete this project.")

    name = project.name
    db.delete(project)
    db.commit()

    return {"message": f"Project '{name}' deleted successfully"}

@router.get("/{project_id}/members", response_model=List[ProjectMemberOut])
def list_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

@router.post("/{project_id}/members", response_model=ProjectMemberOut)
def add_project_member(
    project_id: str,
    member_in: ProjectMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    target_user = db.query(User).filter(User.id == member_in.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_in.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    member = ProjectMember(
        project_id=project_id,
        user_id=member_in.user_id,
        role=member_in.role or "member"
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    log_activity(
        db,
        action="member_added",
        details=f"Added {target_user.full_name} to project",
        user_id=current_user.id,
        project_id=project_id
    )

    return member
