"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { apiRequest } from "@/lib/api";
import { Task, TaskStatus, Project } from "@/lib/types";
import { TaskDetailModal } from "@/components/TaskDetailModal";
import { TaskCreateModal } from "@/components/TaskCreateModal";
import {
  CheckSquare,
  Clock,
  AlertCircle,
  Calendar,
  CheckCircle2,
  Plus,
} from "lucide-react";

export default function MyTasksPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const fetchMyTasks = async () => {
    try {
      const [tList, pList] = await Promise.all([
        apiRequest<Task[]>("/tasks?my_tasks_only=true"),
        apiRequest<Project[]>("/projects"),
      ]);
      setTasks(tList);
      setProjects(pList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    } else if (user) {
      fetchMyTasks();
    }
  }, [user, authLoading]);

  const filteredTasks = tasks.filter((t) => {
    if (statusFilter === "all") return true;
    return t.status === statusFilter;
  });

  const handleToggleTaskStatus = async (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    const newStatus: TaskStatus = task.status === "completed" ? "todo" : "completed";
    try {
      await apiRequest(`/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      fetchMyTasks();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header onOpenCreateTask={() => setIsCreateOpen(true)} />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <CheckSquare className="w-5 h-5 text-indigo-600" />
                <span>My Assigned Tasks</span>
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Tasks allocated to {user?.full_name} across all active projects
              </p>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300"
              >
                <option value="all">All Statuses ({tasks.length})</option>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="in_review">In Review</option>
                <option value="completed">Completed</option>
              </select>

              <button
                onClick={() => setIsCreateOpen(true)}
                className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Task</span>
              </button>
            </div>
          </div>

          {/* Tasks List */}
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading your tasks...</div>
          ) : filteredTasks.length === 0 ? (
            <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
              <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300">
                You're all caught up!
              </h3>
              <p className="text-xs text-slate-500">No tasks currently match this filter.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800/80 shadow-sm overflow-hidden">
              {filteredTasks.map((task) => {
                const isOverdue =
                  task.status !== "completed" &&
                  task.due_date &&
                  new Date(task.due_date) < new Date(new Date().setHours(0, 0, 0, 0));

                return (
                  <div
                    key={task.id}
                    onClick={() => setSelectedTaskId(task.id)}
                    className="p-4 flex items-center justify-between gap-4 hover:bg-slate-50 dark:hover:bg-slate-850 cursor-pointer transition"
                  >
                    <div className="flex items-center gap-3 truncate">
                      <button
                        onClick={(e) => handleToggleTaskStatus(task, e)}
                        className={`w-5 h-5 rounded-md border flex items-center justify-center transition shrink-0 ${
                          task.status === "completed"
                            ? "bg-emerald-500 border-emerald-500 text-white"
                            : "border-slate-300 dark:border-slate-700 hover:border-indigo-500"
                        }`}
                      >
                        {task.status === "completed" && <CheckCircle2 className="w-3.5 h-3.5" />}
                      </button>

                      <div className="truncate">
                        <h4
                          className={`text-xs font-semibold truncate ${
                            task.status === "completed"
                              ? "line-through text-slate-400 dark:text-slate-500"
                              : "text-slate-900 dark:text-slate-100"
                          }`}
                        >
                          {task.title}
                        </h4>
                        <div className="flex items-center gap-2 mt-0.5 text-[10px] text-slate-400">
                          {task.tags && <span>#{task.tags.split(",")[0]}</span>}
                          {task.estimated_hours > 0 && <span>~{task.estimated_hours}h effort</span>}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0 text-xs">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {task.status.replace("_", " ")}
                      </span>

                      <span className="capitalize text-[10px] font-bold text-slate-500 dark:text-slate-400">
                        {task.priority}
                      </span>

                      {task.due_date && (
                        <div
                          className={`flex items-center gap-1 text-[11px] ${
                            isOverdue
                              ? "text-red-600 dark:text-red-400 font-bold"
                              : "text-slate-500 dark:text-slate-400"
                          }`}
                        >
                          {isOverdue ? (
                            <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                          ) : (
                            <Calendar className="w-3.5 h-3.5" />
                          )}
                          <span>
                            {new Date(task.due_date).toLocaleDateString([], {
                              month: "short",
                              day: "numeric",
                            })}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>

      <TaskDetailModal
        taskId={selectedTaskId}
        onClose={() => setSelectedTaskId(null)}
        onTaskUpdated={fetchMyTasks}
        onTaskDeleted={fetchMyTasks}
      />

      <TaskCreateModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onTaskCreated={fetchMyTasks}
        projects={projects}
      />
    </div>
  );
}
