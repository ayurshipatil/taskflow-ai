from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    workspaces,
    projects,
    tasks,
    comments,
    notifications,
    activities,
    analytics,
    ai,
    ws
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Engine"])
api_router.include_router(ws.router, tags=["WebSockets"])
