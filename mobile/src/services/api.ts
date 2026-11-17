import { User, Project, Task, Notification, DashboardMetrics } from "../types";

// When testing on real Android/iOS device or simulator, use local machine IP or localhost
const BASE_URL = "http://localhost:8000/api/v1";

let authToken: string | null = null;
let currentUser: User | null = null;

export const setToken = (token: string, user?: User) => {
  authToken = token;
  if (user) currentUser = user;
};

export const clearToken = () => {
  authToken = null;
  currentUser = null;
};

export const getCurrentUser = () => currentUser;

export async function request<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const res = await fetch(`${BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(errorBody || `HTTP ${res.status}`);
  }

  return res.json();
}

export const authService = {
  login: async (username: string, password: string): Promise<{ access_token: string; user: User }> => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });

    if (!res.ok) {
      throw new Error("Invalid email or password");
    }

    const data = await res.json();
    setToken(data.access_token, data.user);
    return data;
  },
  register: async (payload: { email: string; password: string; full_name: string; role?: string }) => {
    const data = await request<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setToken(data.access_token, data.user);
    return data;
  },
  getProfile: async () => request<User>("/auth/me"),
};

export const taskService = {
  getMyTasks: async () => request<Task[]>("/tasks?my_tasks_only=true"),
  getProjectTasks: async (projectId: string) => request<Task[]>(`/tasks?project_id=${projectId}`),
  getTaskDetail: async (taskId: string) => request<Task>(`/tasks/${taskId}`),
  updateTaskStatus: async (taskId: string, status: string) =>
    request<Task>(`/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  createTask: async (task: Partial<Task>) =>
    request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(task),
    }),
  toggleSubtask: async (subtaskId: string) =>
    request(`/tasks/subtasks/${subtaskId}`, { method: "PATCH" }),
  addComment: async (taskId: string, content: string) =>
    request(`/comments/task/${taskId}`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
};

export const projectService = {
  getProjects: async () => request<Project[]>("/projects"),
  getProject: async (id: string) => request<Project>(`/projects/${id}`),
};

export const aiService = {
  generateTask: async (requirement: string) =>
    request("/ai/generate-tasks", {
      method: "POST",
      body: JSON.stringify({ requirement }),
    }),
  chat: async (message: string, projectId?: string) =>
    request("/ai/assistant-chat", {
      method: "POST",
      body: JSON.stringify({ message, project_id: projectId || null }),
    }),
  getProjectHealth: async (projectId: string) =>
    request(`/ai/project-health/${projectId}`),
};

export const notifService = {
  getNotifications: async () => request<Notification[]>("/notifications?limit=20"),
  markRead: async (id: string) => request(`/notifications/${id}/read`, { method: "PATCH" }),
};
