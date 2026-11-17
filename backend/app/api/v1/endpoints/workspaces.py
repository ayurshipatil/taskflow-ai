from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceOut, WorkspaceUpdate,
    WorkspaceMemberAdd, WorkspaceMemberOut
)

router = APIRouter()

@router.get("", response_model=List[WorkspaceOut])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    workspace_ids = [m.workspace_id for m in memberships]
    workspaces = db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()
    return workspaces

@router.post("", response_model=WorkspaceOut)
def create_workspace(
    workspace_in: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    slug = workspace_in.slug or f"ws-{uuid.uuid4().hex[:8]}"
    existing = db.query(Workspace).filter(Workspace.slug == slug).first()
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    workspace = Workspace(
        name=workspace_in.name,
        slug=slug,
        description=workspace_in.description,
        owner_id=current_user.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=WorkspaceRole.OWNER
    )
    db.add(member)
    db.commit()

    return workspace

@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberOut])
def get_workspace_members(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    return members

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberOut)
def add_workspace_member(
    workspace_id: str,
    member_in: WorkspaceMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    target_user = db.query(User).filter(User.email == member_in.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found with this email.")

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace.")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=member_in.role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
