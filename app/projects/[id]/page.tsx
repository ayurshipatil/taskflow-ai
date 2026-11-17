"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { apiRequest, createWebSocket } from "@/lib/api";
import { Project, Task, TaskStatus, TaskPriority, User } from "@/lib/types";
import { KanbanBoard } from "@/components/KanbanBoard";
import { TaskDetailModal } from "@/components/TaskDetailModal";
import { TaskCreateModal } from "@/components/TaskCreateModal";
import { AITaskGeneratorModal } from "@/components/AITaskGeneratorModal";
import { AIHealthWidget } from "@/components/AIHealthWidget";
import { AIChatDrawer } from "@/components/AIChatDrawer";
import {
  FolderKanban,
  Kanban,
  List,
  Sparkles,
  Users,
  Activity,
  Plus,
  Trash2,
  Calendar,
  CheckCircle2,
  Clock,
  Radio,
  Search,
} from "lucide-react";

type TabType = "kanban" | "list" | "ai_health" | "team" | "activity";

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { user, loading: authLoading } = useAuth();

  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>("kanban");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");

  // Modals state
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false);
  const [defaultTaskStatus, setDefaultTaskStatus] = useState<TaskStatus>("todo");
  const [isAIGeneratorOpen, setIsAIGeneratorOpen] = useState(false);
  const [isAIChatOpen, setIsAIChatOpen] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  const fetchProjectData = async () => {
    try {
      const [proj, tList] = await Promise.all([
        apiRequest<Project>(`/projects/${projectId}`),
        apiRequest<Task[]>(`/tasks?project_id=${projectId}`),
      ]);
      setProject(proj);
      setTasks(tList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    } else if (user && projectId) {
      fetchProjectData();

      // Setup WebSocket connection for live updates
      const ws = createWebSocket(projectId);
      if (ws) {
        ws.onopen = () => setWsConnected(true);
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log("WebSocket event received:", data);
            // Refresh tasks on any mutation
            fetchProjectData();
          } catch (err) {
            console.error("WS error parsing message:", err);
          }
        };
        ws.onclose = () => setWsConnected(false);

        return () => {
          ws.close();
        };
      }
    }
  }, [user, authLoading, projectId]);

  // Kanban drag-and-drop status update
  const handleTaskStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    // Optimistic UI update
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );

    try {
      await apiRequest(`/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      fetchProjectData();
    } catch (e) {
      console.error("Failed to update task status", e);
      fetchProjectData(); // Revert on failure
    }
  };

  const handleDeleteProject = async () => {
    if (!confirm(`Are you sure you want to permanently delete "${project?.name}"?`)) return;
    try {
      await apiRequest(`/projects/${projectId}`, { method: "DELETE" });
      router.push("/projects");
    } catch (e: any) {
      alert(e.message || "Failed to delete project");
    }
  };

  const handleOpenAddTask = (status: TaskStatus = "todo") => {
    setDefaultTaskStatus(status);
    setIsCreateTaskOpen(true);
  };

  // Filter tasks for List view
  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "all" || t.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || t.priority === priorityFilter;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  if (loading || !project) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="text-xs font-semibold text-slate-500 animate-pulse">
          Loading Project Workspace...
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          onOpenCreateTask={() => handleOpenAddTask("todo")}
          onOpenAIGenerator={() => setIsAIGeneratorOpen(true)}
        />

        <main className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Project Title Bar */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900">
                  {project.status}
                </span>
                <span className="text-xs text-slate-400 capitalize">
                  {project.priority} Priority
                </span>

                {/* WebSocket live status indicator */}
                <span
                  title={wsConnected ? "Real-time updates active" : "Connecting real-time..."}
                  className="flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold ml-2"
                >
                  <Radio className="w-3 h-3 text-emerald-500 animate-pulse" />
                  <span>Live Sync</span>
                </span>
              </div>

              <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                {project.name}
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-2xl">
                {project.description || "No description provided."}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsAIGeneratorOpen(true)}
                className="px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-xs font-semibold border border-indigo-200 dark:border-indigo-800 transition flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Generate Tasks</span>
              </button>

              <button
                onClick={() => handleOpenAddTask("todo")}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Task</span>
              </button>

              {user?.role === "admin" || user?.role === "project_manager" ? (
                <button
                  onClick={handleDeleteProject}
                  title="Delete project"
                  className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              ) : null}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1 border-b border-slate-200 dark:border-slate-800 pb-2">
            {[
              { id: "kanban", name: "Kanban Board", icon: Kanban },
              { id: "list", name: "List View", icon: List },
              { id: "ai_health", name: "AI Health Diagnostics", icon: Sparkles },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </div>

          {/* TAB 1: KANBAN BOARD */}
          {activeTab === "kanban" && (
            <div className="h-[calc(100vh-250px)]">
              <KanbanBoard
                tasks={tasks}
                onTaskStatusChange={handleTaskStatusChange}
                onSelectTask={(task) => setSelectedTaskId(task.id)}
                onAddTaskToColumn={(colStatus) => handleOpenAddTask(colStatus)}
              />
            </div>
          )}

          {/* TAB 2: LIST VIEW */}
          {activeTab === "list" && (
            <div className="space-y-3">
              {/* Filter controls */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="relative w-full sm:w-72">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-800 dark:text-slate-200"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-700 dark:text-slate-300"
                  >
                    <option value="all">All Statuses</option>
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="in_review">In Review</option>
                    <option value="completed">Completed</option>
                  </select>

                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-700 dark:text-slate-300"
                  >
                    <option value="all">All Priorities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>

              {/* Tasks Table */}
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="p-3">Title</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Priority</th>
                      <th className="p-3">Due Date</th>
                      <th className="p-3">Effort</th>
                      <th className="p-3">Assignee</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredTasks.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-slate-400">
                          No tasks match filters.
                        </td>
                      </tr>
                    ) : (
                      filteredTasks.map((t) => (
                        <tr
                          key={t.id}
                          onClick={() => setSelectedTaskId(t.id)}
                          className="hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer transition"
                        >
                          <td className="p-3 font-semibold text-slate-900 dark:text-slate-100">
                            {t.title}
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                              {t.status.replace("_", " ")}
                            </span>
                          </td>
                          <td className="p-3">
                            <span className="capitalize font-semibold text-slate-700 dark:text-slate-300">
                              {t.priority}
                            </span>
                          </td>
                          <td className="p-3 text-slate-500">
                            {t.due_date ? new Date(t.due_date).toLocaleDateString([], { month: "short", day: "numeric" }) : "—"}
                          </td>
                          <td className="p-3 text-slate-500">
                            {t.estimated_hours}h
                          </td>
                          <td className="p-3 text-slate-600 dark:text-slate-300 font-medium">
                            {t.assignee?.full_name || "Unassigned"}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: AI HEALTH DIAGNOSTICS */}
          {activeTab === "ai_health" && (
            <AIHealthWidget projectId={projectId} />
          )}
        </main>
      </div>

      {/* Modals */}
      <TaskDetailModal
        taskId={selectedTaskId}
        onClose={() => setSelectedTaskId(null)}
        onTaskUpdated={fetchProjectData}
        onTaskDeleted={fetchProjectData}
      />

      <TaskCreateModal
        isOpen={isCreateTaskOpen}
        onClose={() => setIsCreateTaskOpen(false)}
        onTaskCreated={fetchProjectData}
        projects={project ? [project] : []}
        defaultProjectId={projectId}
        defaultStatus={defaultTaskStatus}
      />

      <AITaskGeneratorModal
        isOpen={isAIGeneratorOpen}
        onClose={() => setIsAIGeneratorOpen(false)}
        onTaskCreated={fetchProjectData}
        projects={project ? [project] : []}
        defaultProjectId={projectId}
      />

      <AIChatDrawer
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
        activeProjectId={projectId}
      />
    </div>
  );
}
