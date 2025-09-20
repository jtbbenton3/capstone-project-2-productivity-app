// Minimal API helper used everywhere
const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5005";

async function request(path, { method = "GET", body, headers } = {}) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...(headers || {}) },
    credentials: "include", // include session cookie
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try { data = await res.json(); } catch (_) { /* ignore */ }

  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

// ----- Auth -----
export const auth = {
  me: () => request("/auth/me"),
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  signup: (username, email, password) => request("/auth/signup", { method: "POST", body: { username, email, password } }),
  logout: () => request("/auth/logout", { method: "POST" }),
};

// ----- Projects -----
export const projects = {
  list: () => request("/projects"),
  create: (title, description) => request("/projects", { method: "POST", body: { title, description } }),
  remove: (id) => request(`/projects/${id}`, { method: "DELETE" }),
};

// ----- Tasks (paginated) -----
export const tasks = {
  list: ({ projectId, page = 1, perPage = 10, status = "all", sort = "due_date" }) =>
    request(`/tasks?project_id=${projectId}&page=${page}&per_page=${perPage}&status=${status}&sort=${sort}`),

  create: ({ projectId, title, dueDate, priority = "normal", status = "todo" }) =>
    request("/tasks", {
      method: "POST",
      body: { project_id: projectId, title, due_date: dueDate, priority, status },
    }),

  update: (id, patch) => request(`/tasks/${id}`, { method: "PATCH", body: patch }),
  remove: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
};

// ----- Subtasks -----
export const subtasks = {
  list: (taskId) => request(`/subtasks?task_id=${taskId}`),
  create: ({ taskId, title }) => request("/subtasks", { method: "POST", body: { task_id: taskId, title } }),
  update: (id, patch) => request(`/subtasks/${id}`, { method: "PATCH", body: patch }),
  remove: (id) => request(`/subtasks/${id}`, { method: "DELETE" }),
};