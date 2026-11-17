# TaskFlow AI — Intelligent Project Management Platform

TaskFlow AI is a modern, production-grade project management and team collaboration platform featuring an asynchronous **FastAPI** backend, **PostgreSQL** database, **Next.js 14** (App Router) web dashboard, **React Native Expo** mobile application, real-time **WebSockets**, and structured **AI Assistant** capabilities.

Designed following sleek SaaS standards inspired by Linear and Notion, TaskFlow AI is built to demonstrate full-stack engineering excellence, scalable relational database modeling, real-time collaboration, and LLM integration.

---

## 🌟 Key Features

### 1. Intelligent AI Assistant Suite
- **AI Task Generator**: Converts natural language feature requirements (e.g., *"Develop user authentication with Google login"*) into structured technical tasks with implementation steps, subtasks, complexity estimates, and acceptance criteria.
- **AI Project Breakdown**: Decomposes high-level project concepts into multi-phase sprint plans with dependencies and imports them directly into projects.
- **AI Project Health Diagnostics**: Evaluates actual database records (completed vs overdue tasks, member workloads, priority congestion) to score project health and formulate corrective actions.
- **Context-Aware Task Assistant Chat**: Answers live queries (*"What should I work on next?"*, *"Summarise my current project"*, *"Check overdue tasks"*) using authenticated workspace context. Includes an intelligent deterministic fallback engine when an LLM API key is unconfigured.

### 2. Project & Task Management
- **Interactive Kanban Board**: Drag-and-drop task progression between *To Do*, *In Progress*, *In Review*, and *Completed* columns with database updates and real-time broadcasts.
- **Interactive List View**: Filter by status, priority, and text search with instant inline status toggling.
- **Task Detail & Discussions**: Subtask checklists, comments feed with real-time sync, priority badges, tags, and effort estimates.

### 3. Real-Time Collaboration & WebSockets
- Changes to tasks or new comments broadcast via WebSockets to all team members viewing the project without refreshing.
- In-app notification center tracking task assignments, status changes, and mentions.

### 4. Visual Analytics (Recharts)
- Task delivery velocity and 7-day completion trends.
- Status and priority distribution breakdowns.
- Team workload and individual productivity charts calculated from live database records.
- Monthly interactive task deadline calendar.

### 5. Multi-Role RBAC & Multi-Tenancy
- **Admin**: Full workspace configuration and user role assignments.
- **Project Manager**: Project planning, sprint creation, and ticket management.
- **Developer**: Assigned deliverables execution and progress reporting.
- **Team Member**: Collaborative commentary and permitted subtask tracking.

### 6. Cross-Platform Mobile Application
- Built with React Native & Expo, sharing the same REST API contracts and authentication session.
- Features mobile dashboard, task toggling, project overview, notifications, and AI Assistant.

---

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| **Web Frontend** | Next.js 14 (App Router), React, TypeScript, Tailwind CSS, Lucide Icons, Recharts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2, WebSockets, Uvicorn |
| **Database** | PostgreSQL / SQLite (via dynamic SQLAlchemy connection), Alembic |
| **Authentication** | JWT (JSON Web Tokens), BCrypt password hashing, RBAC middleware |
| **AI Integration** | OpenAI GPT-4o / Configurable LLM Provider + High-Fidelity Demo Engine |
| **Mobile App** | React Native, Expo, React Navigation, TypeScript |
| **DevOps** | Docker, Docker Compose, Vercel / Render ready |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10+)

### 1. Clone & Setup Workspace
```bash
cd /Users/ayurshipatil/.gemini/antigravity/scratch/taskflow-ai
```

### 2. Start the Backend API Server
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run database setup & start server
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The database automatically creates all relational tables and seeds realistic demo data on startup.*
- **API URL**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/api/v1/docs`

### 3. Start the Next.js Web Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
- **Web Dashboard**: `http://localhost:3000`

### 4. Start the Mobile Expo Application
In a new terminal:
```bash
cd mobile
npm install
npx expo start
```
*Press `w` in terminal to preview in web browser, or scan the QR code with Expo Go on iOS / Android.*

---

## 👥 Demo Accounts

The database comes pre-seeded with 4 test accounts across all roles:

| Role | Email | Password | Name |
|---|---|---|---|
| **Admin** | `admin@taskflow.ai` | `password123` | Elena Vance |
| **Project Manager** | `sarah.pm@taskflow.ai` | `password123` | Sarah Connor |
| **Developer** | `alex.dev@taskflow.ai` | `password123` | Alex Mercer |
| **Team Member** | `emily.team@taskflow.ai` | `password123` | Emily Davis |

*Tip: The web login page features **1-Click Demo Sign In buttons** to test any role with a single click.*

---

## 🐳 Docker Deployment

To launch the complete platform (PostgreSQL + FastAPI + Next.js) with Docker Compose:

```bash
docker-compose up --build
```
- Web Application: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/api/v1/docs`
- PostgreSQL: `localhost:5432`

---

## 🧪 Running Automated Tests

Run backend integration test suite verifying authentication, RBAC, CRUD, and AI endpoints:
```bash
cd backend
PYTHONPATH=. .venv/bin/pytest tests/test_api.py -v
```

---

## 📁 Repository Structure

```
taskflow-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Auth, Projects, Tasks, AI, Analytics, WS
│   │   ├── core/               # Settings, Security (bcrypt/jwt)
│   │   ├── database/           # Session, Table schemas & Seed initialization
│   │   ├── models/             # SQLAlchemy Relational Models
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   └── services/           # AI Engine, Activity Logger, WS Manager
│   ├── tests/                  # Pytest automated test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                    # Next.js App Router (Dashboard, Projects, AI, Analytics)
│   ├── components/             # Kanban, Modals, AI Widgets, Header, Sidebar
│   ├── lib/                    # API client, Auth & Theme contexts, TypeScript types
│   ├── Dockerfile
│   └── package.json
├── mobile/
│   ├── src/
│   │   ├── screens/            # Mobile views (Dashboard, MyTasks, TaskDetail, AI)
│   │   ├── navigation/         # BottomTabs and Stack navigation
│   │   ├── services/           # Shared REST client
│   │   └── types/              # Cross-platform TypeScript definitions
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```
