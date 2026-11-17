from datetime import date, datetime, timedelta
import logging
from app.database.session import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.models.project import Project, ProjectMember, ProjectStatus, ProjectPriority
from app.models.task import Task, Subtask, TaskComment, TaskStatus, TaskPriority
from app.models.notification import Notification, NotificationType
from app.models.activity import ActivityLog

logger = logging.getLogger(__name__)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if database already seeded
    existing_admin = db.query(User).filter(User.email == "admin@taskflow.ai").first()
    if existing_admin:
        logger.info("Database already initialized with seed data.")
        db.close()
        return

    logger.info("Seeding database with professional demonstration data...")

    # 1. Create Users across all roles
    admin = User(
        email="admin@taskflow.ai",
        hashed_password=get_password_hash("password123"),
        full_name="Elena Vance",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        role=UserRole.ADMIN,
        is_active=True
    )
    pm = User(
        email="sarah.pm@taskflow.ai",
        hashed_password=get_password_hash("password123"),
        full_name="Sarah Connor",
        avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
        role=UserRole.PROJECT_MANAGER,
        is_active=True
    )
    dev = User(
        email="alex.dev@taskflow.ai",
        hashed_password=get_password_hash("password123"),
        full_name="Alex Mercer",
        avatar_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80",
        role=UserRole.DEVELOPER,
        is_active=True
    )
    team_member = User(
        email="emily.team@taskflow.ai",
        hashed_password=get_password_hash("password123"),
        full_name="Emily Davis",
        avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80",
        role=UserRole.TEAM_MEMBER,
        is_active=True
    )

    db.add_all([admin, pm, dev, team_member])
    db.commit()
    for u in [admin, pm, dev, team_member]:
        db.refresh(u)

    # 2. Workspace
    workspace = Workspace(
        name="Acme Enterprise Labs",
        slug="acme-enterprise-labs",
        description="Core innovation and delivery workspace for enterprise cloud and mobile products.",
        owner_id=admin.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Workspace Members
    db.add_all([
        WorkspaceMember(workspace_id=workspace.id, user_id=admin.id, role=WorkspaceRole.OWNER),
        WorkspaceMember(workspace_id=workspace.id, user_id=pm.id, role=WorkspaceRole.ADMIN),
        WorkspaceMember(workspace_id=workspace.id, user_id=dev.id, role=WorkspaceRole.MEMBER),
        WorkspaceMember(workspace_id=workspace.id, user_id=team_member.id, role=WorkspaceRole.MEMBER),
    ])
    db.commit()

    # 3. Projects
    today = date.today()
    p1 = Project(
        workspace_id=workspace.id,
        name="TaskFlow Mobile App",
        description="Cross-platform iOS and Android application with real-time sync, offline caching, and push alerts.",
        status=ProjectStatus.ACTIVE,
        priority=ProjectPriority.HIGH,
        start_date=today - timedelta(days=14),
        end_date=today + timedelta(days=30),
        manager_id=pm.id
    )
    p2 = Project(
        workspace_id=workspace.id,
        name="AI Intelligence Engine",
        description="LLM-assisted project health diagnostics, automated sprint planning, and natural language decomposition.",
        status=ProjectStatus.ACTIVE,
        priority=ProjectPriority.CRITICAL,
        start_date=today - timedelta(days=7),
        end_date=today + timedelta(days=21),
        manager_id=pm.id
    )
    p3 = Project(
        workspace_id=workspace.id,
        name="Client Billing & Subscription Portal",
        description="Self-service invoice management, Stripe payment processing, and usage analytics.",
        status=ProjectStatus.PLANNING,
        priority=ProjectPriority.MEDIUM,
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=45),
        manager_id=admin.id
    )
    db.add_all([p1, p2, p3])
    db.commit()
    for p in [p1, p2, p3]:
        db.refresh(p)

    # Project Members
    for p in [p1, p2, p3]:
        db.add_all([
            ProjectMember(project_id=p.id, user_id=admin.id, role="Executive Sponsor"),
            ProjectMember(project_id=p.id, user_id=pm.id, role="Project Manager"),
            ProjectMember(project_id=p.id, user_id=dev.id, role="Senior Engineer"),
            ProjectMember(project_id=p.id, user_id=team_member.id, role="Product Designer")
        ])
    db.commit()

    # 4. Tasks for Project 1: TaskFlow Mobile App
    t1_1 = Task(
        project_id=p1.id,
        title="Setup React Native Expo & Navigation Hub",
        description="Initialize Expo project with TypeScript, configure BottomTabNavigator and authentication guards.",
        status=TaskStatus.COMPLETED,
        priority=TaskPriority.HIGH,
        assignee_id=dev.id,
        start_date=today - timedelta(days=12),
        due_date=today - timedelta(days=8),
        estimated_hours=10,
        tags="mobile,frontend",
        position=1
    )
    t1_2 = Task(
        project_id=p1.id,
        title="Build Mobile Task Detail & Comment View",
        description="Render rich task data, subtask checkboxes, activity timeline, and instant comment posting.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assignee_id=dev.id,
        start_date=today - timedelta(days=5),
        due_date=today + timedelta(days=3),
        estimated_hours=14,
        tags="mobile,ui",
        position=2
    )
    t1_3 = Task(
        project_id=p1.id,
        title="Implement Push Notification Listener",
        description="Integrate Expo Notifications service worker and register device push tokens on backend.",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        assignee_id=team_member.id,
        start_date=today + timedelta(days=2),
        due_date=today + timedelta(days=10),
        estimated_hours=8,
        tags="mobile,notifications",
        position=3
    )
    t1_4 = Task(
        project_id=p1.id,
        title="Offline Data Caching with Async Storage",
        description="Cache project metadata and offline task mutations; replay queue upon reconnecting to network.",
        status=TaskStatus.IN_REVIEW,
        priority=TaskPriority.CRITICAL,
        assignee_id=dev.id,
        start_date=today - timedelta(days=4),
        due_date=today + timedelta(days=1),
        estimated_hours=16,
        tags="mobile,sync",
        position=4
    )
    # Overdue task for realistic testing
    t1_5 = Task(
        project_id=p1.id,
        title="Fix iOS Safe Area & Keyboard Avoiding Layout",
        description="Resolve bottom tab clipping on notched devices and keyboard overlap on input forms.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assignee_id=team_member.id,
        start_date=today - timedelta(days=7),
        due_date=today - timedelta(days=1),  # Overdue!
        estimated_hours=6,
        tags="mobile,bug",
        position=5
    )

    # 5. Tasks for Project 2: AI Intelligence Engine
    t2_1 = Task(
        project_id=p2.id,
        title="Implement Real-Time Project Health Diagnostics",
        description="Aggregate pending tickets, overdue milestones, and workload distribution to generate actionable AI reports.",
        status=TaskStatus.COMPLETED,
        priority=TaskPriority.CRITICAL,
        assignee_id=dev.id,
        start_date=today - timedelta(days=6),
        due_date=today - timedelta(days=2),
        estimated_hours=12,
        tags="backend,ai",
        position=1
    )
    t2_2 = Task(
        project_id=p2.id,
        title="Interactive AI Assistant Chat Assistant",
        description="Provide natural language Q&A for project managers to ask 'What should I work on next?' and risk reviews.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assignee_id=dev.id,
        start_date=today - timedelta(days=2),
        due_date=today + timedelta(days=4),
        estimated_hours=16,
        tags="ai,frontend",
        position=2
    )
    t2_3 = Task(
        project_id=p2.id,
        title="Natural Language Task & Story Breakdown Generator",
        description="Allow product managers to type simple requirements and generate structured tasks with acceptance criteria.",
        status=TaskStatus.COMPLETED,
        priority=TaskPriority.HIGH,
        assignee_id=pm.id,
        start_date=today - timedelta(days=5),
        due_date=today - timedelta(days=1),
        estimated_hours=10,
        tags="ai,pm",
        position=3
    )

    db.add_all([t1_1, t1_2, t1_3, t1_4, t1_5, t2_1, t2_2, t2_3])
    db.commit()
    for t in [t1_1, t1_2, t1_3, t1_4, t1_5, t2_1, t2_2, t2_3]:
        db.refresh(t)

    # 6. Subtasks
    db.add_all([
        Subtask(task_id=t1_2.id, title="Design responsive detail sheet modal", is_completed=True),
        Subtask(task_id=t1_2.id, title="Implement subtask toggle API call", is_completed=True),
        Subtask(task_id=t1_2.id, title="Connect WebSocket for real-time comment feed", is_completed=False),
        Subtask(task_id=t1_4.id, title="Configure AsyncStorage persistent key-value store", is_completed=True),
        Subtask(task_id=t1_4.id, title="Implement optimistic offline mutation queue", is_completed=False),
        Subtask(task_id=t2_2.id, title="Build chat message container with markdown rendering", is_completed=True),
        Subtask(task_id=t2_2.id, title="Add quick action pills (Risk check, Overdue tasks)", is_completed=True),
        Subtask(task_id=t2_2.id, title="Handle network retry and fallback demo state", is_completed=True),
    ])
    db.commit()

    # 7. Comments
    db.add_all([
        TaskComment(
            task_id=t1_2.id,
            user_id=pm.id,
            content="Alex, make sure the task detail sheet supports keyboard dismissing on swipe."
        ),
        TaskComment(
            task_id=t1_2.id,
            user_id=dev.id,
            content="Done! Tested on both iOS Simulator and Android Emulator. Smooth 60fps animations."
        ),
        TaskComment(
            task_id=t1_5.id,
            user_id=pm.id,
            content="Emily, notice this task is 1 day overdue. Do you need any assistance resolving the notch styling?"
        ),
        TaskComment(
            task_id=t1_5.id,
            user_id=team_member.id,
            content="I am wrapping up the React Native SafeAreaProvider patch right now, will push in an hour!"
        )
    ])
    db.commit()

    # 8. Activity Logs
    db.add_all([
        ActivityLog(
            project_id=p1.id,
            task_id=t1_1.id,
            user_id=dev.id,
            action="status_updated",
            details="Moved 'Setup React Native Expo & Navigation Hub' to completed"
        ),
        ActivityLog(
            project_id=p1.id,
            task_id=t1_2.id,
            user_id=pm.id,
            action="comment_added",
            details="Added guidance on swipe gesture keyboard dismiss"
        ),
        ActivityLog(
            project_id=p2.id,
            task_id=t2_1.id,
            user_id=dev.id,
            action="status_updated",
            details="Completed Project Health Diagnostics backend algorithms"
        ),
        ActivityLog(
            project_id=p1.id,
            user_id=admin.id,
            action="project_created",
            details="Initialized TaskFlow Mobile App project"
        )
    ])
    db.commit()

    # 9. Notifications
    db.add_all([
        Notification(
            user_id=dev.id,
            title="Task Assigned",
            message="Sarah Connor assigned you to 'Offline Data Caching with Async Storage'",
            type=NotificationType.TASK_ASSIGNED,
            link=f"/projects/{p1.id}?task={t1_4.id}",
            is_read=False
        ),
        Notification(
            user_id=team_member.id,
            title="Overdue Task Alert",
            message="Task 'Fix iOS Safe Area & Keyboard Avoiding Layout' is past its scheduled deadline",
            type=NotificationType.OVERDUE,
            link=f"/projects/{p1.id}?task={t1_5.id}",
            is_read=False
        ),
        Notification(
            user_id=dev.id,
            title="New Comment",
            message="Sarah Connor commented on 'Build Mobile Task Detail & Comment View'",
            type=NotificationType.COMMENT_ADDED,
            link=f"/projects/{p1.id}?task={t1_2.id}",
            is_read=True
        )
    ])
    db.commit()
    db.close()
    logger.info("Database seeding successfully completed!")
