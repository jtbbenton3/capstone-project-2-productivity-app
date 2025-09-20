// client/src/api.js

// Base API URL (falls back to localhost if .env isn't loaded)
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5005";

// Small JSON fetch wrapper
async function request(path, { method = "GET", body, headers } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
    credentials: "include", // send cookies for session auth
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch (_) {}

  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return data;
}

export const api = {
  // ---- Auth ----
  me() {
    return request("/auth/me");
    
  },
  signup({ username, email, password }) {
    // Backend expects these three fields
    return request("/auth/signup", {
      method: "POST",
      body: { username, email, password },
    });
  },
  login({ email, password }) {
    return request("/auth/login", {
      method: "POST",
      body: { email, password },
    });
  },
  logout() {
    return request("/auth/logout", { method: "POST" });
  },

  // ---- Projects/Tasks ----
  createProject({ title, description }) {
    return request("/projects", { method: "POST", body: { title, description } });
    
  },
  deleteProject(id) {
    return request(`/projects/${id}`, { method: "DELETE" });
  },
  listTasks({ project_id, page = 1, per_page = 10, sort } = {}) {
    const params = new URLSearchParams();
    if (project_id) params.set("project_id", project_id);
    if (page) params.set("page", page);
    if (per_page) params.set("per_page", per_page);
    if (sort) params.set("sort", sort);
    return request(`/tasks?${params.toString()}`);
    
  },
  createTask({ project_id, title, due_date, priority = "normal", status = "todo" }) {
    return request("/tasks", {
      method: "POST",
      body: { project_id, title, due_date, priority, status },
    });
  },
};

export default api;