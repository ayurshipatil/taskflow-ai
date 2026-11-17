export type UserRole = "admin" | "project_manager" | "developer" | "team_member";

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: UserRole;
  is_active: boolean;
}

export type TaskStatus = "todo" | "in_progress" | "in_review" | "completed";
export type TaskPriority = "low" | "medium" | "high" | "critical";

export interface Subtask {
  id: string;
  task_id: string;
  title: string;
  is_completed: boolean;
}

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id?: string;
  assignee?: User;
  due_date?: string;
  estimated_hours: number;
  tags?: string;
  subtasks: Subtask[];
  comments_count: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  priority: string;
  task_count: number;
  completed_task_count: number;
  progress_percentage: number;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

export interface DashboardMetrics {
  total_projects: number;
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
}
