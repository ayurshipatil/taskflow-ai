from typing import List, Optional
from pydantic import BaseModel
from app.models.task import TaskPriority

class TaskGeneratorRequest(BaseModel):
    requirement: str
    project_id: Optional[str] = None

class GeneratedSubtask(BaseModel):
    title: str

class GeneratedTaskResponse(BaseModel):
    title: str
    description: str
    implementation_steps: List[str]
    subtasks: List[str]
    suggested_priority: TaskPriority
    estimated_complexity: str  # e.g., Low, Medium, High, Story Points / Hours
    estimated_hours: int
    acceptance_criteria: List[str]
    tags: List[str]
    is_demo_mode: bool = False

class ProjectBreakdownRequest(BaseModel):
    project_idea: str
    workspace_id: Optional[str] = None

class BreakdownTask(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    estimated_hours: int
    suggested_days_from_start: int
    subtasks: List[str] = []

class ProjectPhase(BaseModel):
    phase_name: str
    tasks: List[BreakdownTask]

class ProjectBreakdownResponse(BaseModel):
    project_name: str
    project_objectives: List[str]
    phases: List[ProjectPhase]
    recommended_priorities: List[str]
    is_demo_mode: bool = False

class RiskItem(BaseModel):
    severity: str  # Critical, High, Medium, Low
    category: str  # Schedule, Workload, Scope, Quality
    description: str
    impact: str

class RecommendationItem(BaseModel):
    action: str
    priority: str
    rationale: str

class ProjectHealthResponse(BaseModel):
    project_id: str
    project_name: str
    overall_health: str  # On Track, At Risk, Critical
    health_score: int  # 0 to 100
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_percentage: float
    potential_risks: List[RiskItem]
    workload_concerns: List[str]
    recommended_actions: List[RecommendationItem]
    is_demo_mode: bool = False

class AIChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None

class AIChatResponse(BaseModel):
    reply: str
    context_used: Optional[str] = None
    suggested_actions: List[str] = []
    is_demo_mode: bool = False
