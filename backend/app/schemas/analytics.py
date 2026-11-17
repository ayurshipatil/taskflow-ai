from typing import List, Dict, Any
from pydantic import BaseModel

class StatusCount(BaseModel):
    status: str
    count: int

class PriorityCount(BaseModel):
    priority: str
    count: int

class MemberWorkload(BaseModel):
    user_id: str
    name: str
    assigned_count: int
    completed_count: int

class TaskCompletionTrend(BaseModel):
    date: str
    completed: int
    created: int

class DashboardMetrics(BaseModel):
    total_projects: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_rate: float
    status_distribution: List[StatusCount]
    priority_distribution: List[PriorityCount]
    workload: List[MemberWorkload]
    completion_trend: List[TaskCompletionTrend]
