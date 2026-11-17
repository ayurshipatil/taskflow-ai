import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.init_db import init_db

init_db()
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "TaskFlow AI" in data["service"]

def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@taskflow.ai"
    assert data["user"]["role"] == "admin"

def test_login_invalid():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_current_user_and_workspaces():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "admin@taskflow.ai"

    ws_res = client.get("/api/v1/workspaces", headers=headers)
    assert ws_res.status_code == 200
    workspaces = ws_res.json()
    assert len(workspaces) >= 1

def test_projects_and_tasks_crud():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List projects
    proj_res = client.get("/api/v1/projects", headers=headers)
    assert proj_res.status_code == 200
    projects = proj_res.json()
    assert len(projects) >= 1
    project_id = projects[0]["id"]

    # List tasks in project
    task_res = client.get(f"/api/v1/tasks?project_id={project_id}", headers=headers)
    assert task_res.status_code == 200
    tasks = task_res.json()
    assert len(tasks) >= 1

    # Create new task
    new_task_res = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={
            "project_id": project_id,
            "title": "Automated Test Task",
            "description": "Verifying CRUD operations",
            "priority": "high",
            "status": "todo",
            "estimated_hours": 4
        }
    )
    assert new_task_res.status_code == 200
    created_task = new_task_res.json()
    task_id = created_task["id"]
    assert created_task["title"] == "Automated Test Task"

    # Update task (Kanban status transition)
    update_res = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=headers,
        json={"status": "in_progress"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "in_progress"

    # Add comment to task
    comment_res = client.post(
        f"/api/v1/comments/task/{task_id}",
        headers=headers,
        json={"content": "Automated verification comment"}
    )
    assert comment_res.status_code == 200
    assert comment_res.json()["content"] == "Automated verification comment"

    # Delete task
    del_res = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 200

def test_ai_task_generator_and_health():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test AI Task Generator
    gen_res = client.post(
        "/api/v1/ai/generate-tasks",
        headers=headers,
        json={"requirement": "Develop user authentication system with Google login"}
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert "title" in gen_data
    assert "implementation_steps" in gen_data
    assert len(gen_data["subtasks"]) >= 1
    assert "acceptance_criteria" in gen_data

    # Test AI Project Health
    proj_res = client.get("/api/v1/projects", headers=headers)
    project_id = proj_res.json()[0]["id"]
    health_res = client.get(f"/api/v1/ai/project-health/{project_id}", headers=headers)
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert "overall_health" in health_data
    assert "potential_risks" in health_data
    assert "recommended_actions" in health_data

def test_analytics_dashboard():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@taskflow.ai", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_projects"] >= 1
    assert data["total_tasks"] >= 1
    assert len(data["status_distribution"]) > 0
    assert len(data["priority_distribution"]) > 0
    assert len(data["workload"]) > 0
