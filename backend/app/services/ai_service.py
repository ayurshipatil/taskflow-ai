import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import httpx
from app.core.config import settings
from app.models.task import TaskPriority
from app.schemas.ai import (
    GeneratedTaskResponse,
    ProjectBreakdownResponse,
    ProjectPhase,
    BreakdownTask,
    ProjectHealthResponse,
    RiskItem,
    RecommendationItem,
    AIChatResponse
)

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def _is_api_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("sk-placeholder"))

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not self._is_api_configured():
            return None
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.4
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"LLM API returned status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to query LLM API: {e}")
            return None

    async def generate_task(self, requirement: str) -> GeneratedTaskResponse:
        system_prompt = (
            "You are an expert technical product manager and architect. "
            "Given a feature requirement, generate a structured task breakdown. "
            "Output MUST be valid JSON matching this schema: "
            "{"
            "'title': string, "
            "'description': string, "
            "'implementation_steps': list of strings, "
            "'subtasks': list of strings, "
            "'suggested_priority': 'low' | 'medium' | 'high' | 'critical', "
            "'estimated_complexity': 'Low' | 'Medium' | 'High', "
            "'estimated_hours': integer, "
            "'acceptance_criteria': list of strings, "
            "'tags': list of strings"
            "}"
        )
        user_prompt = f"Requirement: {requirement}"

        llm_raw = await self._call_llm(system_prompt, user_prompt)
        if llm_raw:
            try:
                data = json.loads(llm_raw)
                prio_str = data.get("suggested_priority", "medium").lower()
                priority = TaskPriority(prio_str) if prio_str in [p.value for p in TaskPriority] else TaskPriority.MEDIUM
                return GeneratedTaskResponse(
                    title=data.get("title", f"Implement: {requirement[:40]}"),
                    description=data.get("description", requirement),
                    implementation_steps=data.get("implementation_steps", ["Analyze requirements", "Implement changes", "Write tests"]),
                    subtasks=data.get("subtasks", ["Design UI", "Implement backend logic", "QA validation"]),
                    suggested_priority=priority,
                    estimated_complexity=data.get("estimated_complexity", "Medium"),
                    estimated_hours=int(data.get("estimated_hours", 8)),
                    acceptance_criteria=data.get("acceptance_criteria", ["Feature operates as expected without regressions."]),
                    tags=data.get("tags", ["feature", "engineering"]),
                    is_demo_mode=False
                )
            except Exception as e:
                logger.warning(f"Error parsing LLM response: {e}, falling back to demo mode.")

        # High-Fidelity Demo Fallback Engine
        title = requirement.strip()
        if not title.lower().startswith(("build", "create", "implement", "develop", "setup")):
            title = f"Implement {requirement.strip()}"

        tags = ["engineering", "ai-generated"]
        lower_req = requirement.lower()
        if "auth" in lower_req or "login" in lower_req or "security" in lower_req:
            priority = TaskPriority.HIGH
            complexity = "High"
            hours = 16
            tags.extend(["security", "auth"])
            steps = [
                "Configure OAuth 2.0 / OpenID Connect provider credentials in developer console",
                "Create backend token exchange endpoints and verify JWT signatures",
                "Implement user session handling, secure cookie/token storage, and refresh cycle",
                "Build responsive UI login modal with provider button and accessible states",
                "Write automated unit tests for callback validations and error handlers"
            ]
            subtasks = [
                "Configure client ID and secrets in environment variables",
                "Create JWT validation middleware",
                "Implement frontend login button and redirect callback",
                "Test error cases (expired token, network failure)"
            ]
            criteria = [
                "Users can successfully authenticate and obtain valid JWT",
                "Invalid tokens result in HTTP 401 Unauthorized",
                "Session persists across page reloads seamlessly",
                "Passes security audit for CSRF and credential injection"
            ]
        elif "payment" in lower_req or "stripe" in lower_req:
            priority = TaskPriority.CRITICAL
            complexity = "High"
            hours = 24
            tags.extend(["billing", "payments"])
            steps = [
                "Initialize payment gateway SDK and setup webhook signing secret",
                "Create checkout session API endpoint with line-item validation",
                "Handle asynchronous webhook events (payment_succeeded, failed)",
                "Update database subscription status and send customer receipt",
                "Simulate failed card and dispute flows in sandbox environment"
            ]
            subtasks = [
                "Create Stripe customer & checkout session",
                "Implement webhook endpoint with signature verification",
                "Render checkout UI and payment status banner",
                "End-to-end sandbox verification"
            ]
            criteria = [
                "Successful payment updates workspace tier immediately",
                "Webhook idempotency is properly enforced",
                "PCI DSS compliance maintained by never storing raw card numbers"
            ]
        else:
            priority = TaskPriority.MEDIUM
            complexity = "Medium"
            hours = 8
            tags.extend(["feature"])
            steps = [
                f"Define technical specifications and API contracts for {requirement[:50]}",
                "Build scalable database models, migrations, and repository queries",
                "Implement REST endpoints with Pydantic validation and error handling",
                "Construct modern frontend components following design tokens and accessibility",
                "Execute integration tests and end-to-end regression validation"
            ]
            subtasks = [
                "Design component architecture & API schema",
                "Implement backend endpoint logic",
                "Build user-facing interface and responsive layout",
                "Verify test coverage and edge cases"
            ]
            criteria = [
                f"Core requirement fulfilled: '{requirement}'",
                "All edge cases and validation errors provide intuitive user feedback",
                "Performance benchmarks met (<100ms API response time)"
            ]

        return GeneratedTaskResponse(
            title=title,
            description=f"Automated AI specification for: {requirement}.\n\nThis task provides end-to-end guidance from architectural definition to implementation and automated verification.",
            implementation_steps=steps,
            subtasks=subtasks,
            suggested_priority=priority,
            estimated_complexity=complexity,
            estimated_hours=hours,
            acceptance_criteria=criteria,
            tags=tags,
            is_demo_mode=True
        )

    async def breakdown_project(self, project_idea: str) -> ProjectBreakdownResponse:
        system_prompt = (
            "You are a principal software architect and technical project manager. "
            "Break down the given project idea into structured phases with actionable tasks. "
            "Output must be valid JSON matching: "
            "{"
            "'project_name': string, "
            "'project_objectives': list of strings, "
            "'recommended_priorities': list of strings, "
            "'phases': ["
            "  {'phase_name': string, 'tasks': ["
            "     {'title': string, 'description': string, 'priority': 'low'|'medium'|'high'|'critical', 'estimated_hours': int, 'suggested_days_from_start': int, 'subtasks': list of strings}"
            "  ]}"
            "]"
            "}"
        )
        llm_raw = await self._call_llm(system_prompt, f"Project idea: {project_idea}")
        if llm_raw:
            try:
                data = json.loads(llm_raw)
                phases = []
                for p in data.get("phases", []):
                    tasks = []
                    for t in p.get("tasks", []):
                        prio_str = t.get("priority", "medium").lower()
                        prio = TaskPriority(prio_str) if prio_str in [x.value for x in TaskPriority] else TaskPriority.MEDIUM
                        tasks.append(BreakdownTask(
                            title=t.get("title", "Task"),
                            description=t.get("description", ""),
                            priority=prio,
                            estimated_hours=int(t.get("estimated_hours", 8)),
                            suggested_days_from_start=int(t.get("suggested_days_from_start", 1)),
                            subtasks=t.get("subtasks", [])
                        ))
                    phases.append(ProjectPhase(phase_name=p.get("phase_name", "Phase"), tasks=tasks))

                return ProjectBreakdownResponse(
                    project_name=data.get("project_name", project_idea[:40]),
                    project_objectives=data.get("project_objectives", ["Build scalable MVP", "Ensure reliability"]),
                    phases=phases,
                    recommended_priorities=data.get("recommended_priorities", ["Core Architecture", "Feature Velocity", "Security"]),
                    is_demo_mode=False
                )
            except Exception as e:
                logger.warning(f"Error parsing LLM project breakdown: {e}")

        # Deterministic High-Quality Fallback Breakdown
        name = project_idea.strip()
        if not any(name.lower().startswith(x) for x in ["project", "platform", "system"]):
            name = f"{name.title()} Platform"

        phases = [
            ProjectPhase(
                phase_name="Phase 1: Architecture & Foundations",
                tasks=[
                    BreakdownTask(
                        title="Repository Setup & Monorepo Architecture",
                        description="Configure TypeScript, FastAPI, database migrations, CI/CD pipelines and linting standards.",
                        priority=TaskPriority.HIGH,
                        estimated_hours=12,
                        suggested_days_from_start=2,
                        subtasks=["Setup git hooks", "Configure Docker files", "Configure lint and formatting"]
                    ),
                    BreakdownTask(
                        title="Database Schema Design & Migration Pipeline",
                        description="Design relational entities, foreign keys, indexes, and write initial Alembic migrations.",
                        priority=TaskPriority.CRITICAL,
                        estimated_hours=16,
                        suggested_days_from_start=4,
                        subtasks=["Define ERD", "Setup database connection pooling", "Test migration rollback"]
                    ),
                    BreakdownTask(
                        title="Authentication, Sessions & RBAC",
                        description="Implement JWT tokens, bcrypt password hashing, and role-based permissions.",
                        priority=TaskPriority.HIGH,
                        estimated_hours=14,
                        suggested_days_from_start=6,
                        subtasks=["Register & Login endpoints", "OAuth2 security handler", "Frontend auth provider"]
                    )
                ]
            ),
            ProjectPhase(
                phase_name="Phase 2: Core Domain Features",
                tasks=[
                    BreakdownTask(
                        title="Core Business Logic & API Endpoints",
                        description=f"Implement backend services and REST endpoints specifically addressing: {project_idea}",
                        priority=TaskPriority.HIGH,
                        estimated_hours=24,
                        suggested_days_from_start=12,
                        subtasks=["Design API contracts", "Build CRUD operations", "Implement validation logic"]
                    ),
                    BreakdownTask(
                        title="Responsive Web Dashboard & User Workflows",
                        description="Build intuitive UI screens, state management, form validations, and interactive components.",
                        priority=TaskPriority.HIGH,
                        estimated_hours=28,
                        suggested_days_from_start=18,
                        subtasks=["Dashboard metrics view", "List and Kanban views", "Interactive modal workflows"]
                    )
                ]
            ),
            ProjectPhase(
                phase_name="Phase 3: Real-Time Collaboration & Analytics",
                tasks=[
                    BreakdownTask(
                        title="WebSocket Hub & Live Collaboration",
                        description="Enable real-time push updates for changes, notifications, and interactive discussions.",
                        priority=TaskPriority.MEDIUM,
                        estimated_hours=16,
                        suggested_days_from_start=22,
                        subtasks=["WebSocket manager", "Client reconnection handler", "Optimistic UI updates"]
                    ),
                    BreakdownTask(
                        title="Interactive Analytics & Reporting Dashboard",
                        description="Render completion velocity, workload distribution charts, and project milestones.",
                        priority=TaskPriority.MEDIUM,
                        estimated_hours=14,
                        suggested_days_from_start=26,
                        subtasks=["Aggregate query endpoints", "Recharts visual charts", "Export summary"]
                    )
                ]
            ),
            ProjectPhase(
                phase_name="Phase 4: QA, Security Hardening & Release",
                tasks=[
                    BreakdownTask(
                        title="End-to-End Testing & Security Audit",
                        description="Run automated integration tests, penetration testing, input sanitization checks, and performance profiling.",
                        priority=TaskPriority.CRITICAL,
                        estimated_hours=16,
                        suggested_days_from_start=30,
                        subtasks=["Write backend integration tests", "Run frontend Cypress/Jest tests", "Security check"]
                    ),
                    BreakdownTask(
                        title="Production Deployment & Monitoring",
                        description="Deploy Docker containers, configure environment variables, setup health checks and error telemetry.",
                        priority=TaskPriority.HIGH,
                        estimated_hours=10,
                        suggested_days_from_start=32,
                        subtasks=["Deploy to cloud host", "Configure SSL certificates", "Verify uptime monitoring"]
                    )
                ]
            )
        ]

        return ProjectBreakdownResponse(
            project_name=name,
            project_objectives=[
                f"Deliver complete solution for '{project_idea}' with high quality",
                "Achieve robust real-time synchronization and high team velocity",
                "Ensure resilient security, zero data loss, and predictable delivery milestones"
            ],
            phases=phases,
            recommended_priorities=["Foundation & Data Integrity", "Core User Experience", "Deployment & Verification"],
            is_demo_mode=True
        )

    def analyze_project_health(
        self,
        project_name: str,
        project_id: str,
        total_tasks: int,
        completed_tasks: int,
        pending_tasks: int,
        overdue_tasks: int,
        high_priority_pending: int,
        member_count: int,
        unassigned_tasks: int
    ) -> ProjectHealthResponse:
        # Calculate real database metrics
        completion_pct = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

        risks: List[RiskItem] = []
        recommendations: List[RecommendationItem] = []
        workload_concerns: List[str] = []

        # Determine health status based on real numbers
        health_score = 100
        if total_tasks == 0:
            overall_health = "Planning"
            health_score = 80
            recommendations.append(RecommendationItem(
                action="Define initial deliverables and milestones",
                priority="High",
                rationale="The project contains no tasks yet. Use the AI Task Generator to define initial tickets."
            ))
        else:
            if overdue_tasks > 0:
                health_score -= (overdue_tasks * 15)
                risks.append(RiskItem(
                    severity="Critical" if overdue_tasks >= 3 else "High",
                    category="Schedule",
                    description=f"{overdue_tasks} task(s) have passed their due dates without completion.",
                    impact="Blocks downstream deliverables and risks project milestone slip."
                ))
                recommendations.append(RecommendationItem(
                    action=f"Reschedule or reassign the {overdue_tasks} overdue task(s)",
                    priority="Critical",
                    rationale="Overdue tasks impair team velocity and signal delivery bottleneck."
                ))

            if high_priority_pending > (pending_tasks / 2) and high_priority_pending > 2:
                health_score -= 15
                risks.append(RiskItem(
                    severity="High",
                    category="Scope & Priority",
                    description=f"{high_priority_pending} tasks are marked High or Critical priority.",
                    impact="High-priority congestion can lead to team burnout and decision fatigue."
                ))
                recommendations.append(RecommendationItem(
                    action="Re-evaluate priority triage",
                    priority="High",
                    rationale="Not all tasks can be top priority simultaneously. Distribute work into phased sprints."
                ))

            if unassigned_tasks > 0:
                health_score -= (unassigned_tasks * 5)
                workload_concerns.append(f"{unassigned_tasks} task(s) currently have no assignee assigned.")
                recommendations.append(RecommendationItem(
                    action="Assign unallocated tasks to active team members",
                    priority="Medium",
                    rationale="Unassigned tasks remain stagnant and are often forgotten."
                ))

            if member_count > 0 and (pending_tasks / member_count) > 7:
                workload_concerns.append(f"High task-to-member ratio ({round(pending_tasks / member_count, 1)} tasks per member).")
                recommendations.append(RecommendationItem(
                    action="Balance workload or onboard additional developers",
                    priority="Medium",
                    rationale="Heavy task loads increase error rates and development cycle time."
                ))

        health_score = max(10, min(100, health_score))

        if health_score >= 80:
            overall_health = "On Track"
        elif health_score >= 50:
            overall_health = "At Risk"
        else:
            overall_health = "Critical"

        if not recommendations:
            recommendations.append(RecommendationItem(
                action="Maintain current sprint pace and monitor weekly burndown",
                priority="Low",
                rationale="Project metrics indicate strong momentum and healthy team allocation."
            ))

        return ProjectHealthResponse(
            project_id=project_id,
            project_name=project_name,
            overall_health=overall_health,
            health_score=health_score,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
            completion_percentage=completion_pct,
            potential_risks=risks,
            workload_concerns=workload_concerns,
            recommended_actions=recommendations,
            is_demo_mode=not self._is_api_configured()
        )

    async def chat_assistant(
        self,
        user_message: str,
        user_name: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> AIChatResponse:
        system_prompt = (
            "You are TaskFlow AI, an intelligent project management assistant. "
            "You help users manage projects, track tasks, suggest next actions, analyze risks, "
            "and optimize team productivity. Be concise, actionable, and professional. "
            "Format your reply in clean markdown. Provide 2 to 3 suggested follow-up actions."
        )

        context_summary = "No specific project selected."
        if project_context:
            context_summary = (
                f"Project: {project_context.get('name')}\n"
                f"Status: {project_context.get('status')}\n"
                f"Total Tasks: {project_context.get('total_tasks')}\n"
                f"Pending Tasks: {project_context.get('pending_tasks')}\n"
                f"Overdue Tasks: {project_context.get('overdue_tasks')}\n"
                f"My Assigned Tasks: {project_context.get('my_tasks_count')}"
            )

        user_prompt = f"User: {user_name}\nContext:\n{context_summary}\n\nQuestion: {user_message}"

        llm_raw = await self._call_llm(system_prompt, user_prompt)
        if llm_raw:
            try:
                # LLM response
                return AIChatResponse(
                    reply=llm_raw,
                    context_used=context_summary,
                    suggested_actions=[
                        "View overdue tasks",
                        "Generate new task specification",
                        "Run project health analysis"
                    ],
                    is_demo_mode=False
                )
            except Exception:
                pass

        # Intelligent Context-Aware Fallback Engine
        msg = user_message.lower()
        if "what should i work on" in msg or "next" in msg or "my tasks" in msg:
            reply = (
                f"Hello **{user_name}**, based on your active project records:\n\n"
                f"1. **Tackle critical blockers first**: Check any tasks marked `Critical` or `High` priority.\n"
                f"2. **Resolve overdue items**: If you have tasks past their due date, update their status or request a date extension.\n"
                f"3. **In-Progress velocity**: Focus on moving currently assigned `In Progress` items to `In Review` before picking up new tickets from `To Do`."
            )
            actions = ["Filter tasks by My Assigned", "Move task to In Progress", "Open Kanban Board"]
        elif "overdue" in msg:
            overdue_cnt = project_context.get('overdue_tasks', 0) if project_context else 0
            if overdue_cnt > 0:
                reply = (
                    f"⚠️ There are **{overdue_cnt} overdue task(s)** requiring immediate attention.\n\n"
                    f"Recommended actions:\n"
                    f"- Contact the assigned team members to assess blockers.\n"
                    f"- Update the due dates if estimates shifted.\n"
                    f"- Decompose the tasks into smaller subtasks to regain momentum."
                )
            else:
                reply = "🎉 Great news! There are **no overdue tasks** currently in this project. All deliverables are on schedule."
            actions = ["View overdue tasks", "Reschedule deadlines", "Review sprint backlog"]
        elif "summarise" in msg or "summary" in msg or "current project" in msg:
            p_name = project_context.get('name', 'Active Project') if project_context else "your workspace"
            tot = project_context.get('total_tasks', 0) if project_context else 0
            comp = project_context.get('completed_tasks', 0) if project_context else 0
            pend = project_context.get('pending_tasks', 0) if project_context else 0
            reply = (
                f"### Project Summary: **{p_name}**\n\n"
                f"- **Total Scope**: {tot} tasks defined\n"
                f"- **Completed**: {comp} tasks ({round(comp/tot*100 if tot > 0 else 0)}%)\n"
                f"- **Pending / In Flight**: {pend} tasks\n\n"
                f"The team is actively executing deliverables. Review the Kanban board to track workflow distribution."
            )
            actions = ["Open Analytics Dashboard", "Analyze Project Health", "Export status report"]
        elif "risk" in msg:
            reply = (
                "### Primary Project Risk Assessment:\n\n"
                "1. **Scope Creep**: Ensure new requirements are logged as discrete tickets with effort estimates.\n"
                "2. **Resource Bottlenecks**: Avoid concentrating all high-priority tasks onto single team members.\n"
                "3. **Dependency Chains**: Ensure backend APIs are finalized before frontend integration begins."
            )
            actions = ["Run Full Project Health Analysis", "Review Task Priorities", "Audit Team Workload"]
        else:
            reply = (
                f"Hello **{user_name}**! I am your **TaskFlow AI Assistant**.\n\n"
                f"I can help you with:\n"
                f"- **Task Generation**: Type any feature idea to generate a complete specification with steps and acceptance criteria.\n"
                f"- **Project Breakdown**: Transform high-level concepts into multi-phase implementation plans.\n"
                f"- **Health Analysis**: Inspect real database metrics for schedule risks and workload bottlenecks.\n"
                f"- **Work Planning**: Ask *'What should I work on next?'* or *'Summarise my project'* anytime."
            )
            actions = ["Generate new task", "Breakdown new project", "Inspect project health"]

        return AIChatResponse(
            reply=reply,
            context_used=context_summary,
            suggested_actions=actions,
            is_demo_mode=True
        )

ai_service = AIService()
