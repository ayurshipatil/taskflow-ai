"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { apiRequest } from "@/lib/api";
import { Task, Project } from "@/lib/types";
import { TaskDetailModal } from "@/components/TaskDetailModal";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock,
  CheckCircle2,
} from "lucide-react";

export default function CalendarPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("all");
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());

  const fetchTasks = async () => {
    try {
      const [tList, pList] = await Promise.all([
        apiRequest<Task[]>("/tasks"),
        apiRequest<Project[]>("/projects"),
      ]);
      setTasks(tList);
      setProjects(pList);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    } else if (user) {
      fetchTasks();
    }
  }, [user, authLoading]);

  // Calendar calculations
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const filteredTasks = tasks.filter((t) => {
    if (selectedProjectId === "all") return true;
    return t.project_id === selectedProjectId;
  });

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <CalendarDays className="w-5 h-5 text-indigo-600" />
                <span>Task & Deadline Calendar</span>
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Visual delivery schedule and upcoming project milestones
              </p>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={selectedProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300"
              >
                <option value="all">All Projects ({tasks.length} tasks)</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>

              <div className="flex items-center gap-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-1">
                <button
                  onClick={prevMonth}
                  className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs font-bold px-2 text-slate-800 dark:text-slate-200 min-w-[120px] text-center">
                  {monthNames[month]} {year}
                </span>
                <button
                  onClick={nextMonth}
                  className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Monthly Calendar Grid */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            {/* Day of Week Headers */}
            <div className="grid grid-cols-7 border-b border-slate-200 dark:border-slate-800 text-center py-2.5 bg-slate-50 dark:bg-slate-800/40 text-xs font-bold text-slate-500">
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                <div key={day}>{day}</div>
              ))}
            </div>

            {/* Days Matrix */}
            <div className="grid grid-cols-7 auto-rows-fr divide-x divide-y divide-slate-100 dark:divide-slate-800/80 min-h-[500px]">
              {/* Empty padding slots for days before 1st of month */}
              {Array.from({ length: firstDayOfMonth }).map((_, i) => (
                <div key={`empty-${i}`} className="p-2 bg-slate-50/40 dark:bg-slate-950/20" />
              ))}

              {/* Month Days */}
              {Array.from({ length: daysInMonth }).map((_, i) => {
                const dayNumber = i + 1;
                // Format YYYY-MM-DD
                const dayStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayNumber).padStart(2, "0")}`;
                const dayTasks = filteredTasks.filter((t) => t.due_date === dayStr);
                const isToday =
                  new Date().toDateString() === new Date(year, month, dayNumber).toDateString();

                return (
                  <div
                    key={dayNumber}
                    className={`p-2 min-h-[90px] flex flex-col justify-between hover:bg-indigo-50/20 dark:hover:bg-indigo-950/10 transition ${
                      isToday ? "bg-indigo-50/40 dark:bg-indigo-950/20" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-xs font-bold ${
                          isToday
                            ? "w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px]"
                            : "text-slate-700 dark:text-slate-300"
                        }`}
                      >
                        {dayNumber}
                      </span>
                    </div>

                    {/* Task pills on this date */}
                    <div className="space-y-1 mt-1 flex-1 overflow-y-auto max-h-20">
                      {dayTasks.map((t) => (
                        <div
                          key={t.id}
                          onClick={() => setSelectedTaskId(t.id)}
                          className={`px-1.5 py-0.5 rounded text-[10px] font-semibold truncate cursor-pointer transition ${
                            t.status === "completed"
                              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 line-through"
                              : "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-300 hover:bg-indigo-200"
                          }`}
                        >
                          {t.title}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </main>
      </div>

      <TaskDetailModal
        taskId={selectedTaskId}
        onClose={() => setSelectedTaskId(null)}
        onTaskUpdated={fetchTasks}
        onTaskDeleted={fetchTasks}
      />
    </div>
  );
}
