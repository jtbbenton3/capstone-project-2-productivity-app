// small helper around fetch
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5005";

async function request(path, { method = "GET", body, headers } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
    credentials: "include", // send cookies
    body: body ? JSON.stringify(body) : undefined,
  });

  // try to parse json
  let data = null;
  try {
    data = await res.json();
  } catch (_) {
    
  }

  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return data;
}

const api = {
  // auth
  me() {
    return request("/auth/me");
  },
  signup({ username, email, password }) {
    return request("/auth/signup", {
      method: "POST",
      body: { username, email, password },
    });
  },
  login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: { email, password },
    });
  },
  logout() {
    return request("/auth/logout", { method: "POST" });
  },

  // projects
  listProjects() {
    return request("/projects"); 
  },
  createProject({ title, description }) {
    return request("/projects", { method: "POST", body: { title, description } });
  },
  deleteProject(id) {
    return request(`/projects/${id}`, { method: "DELETE" });
  },

  // tasks
  listTasks({ project_id, sort = "due_date", page = 1, per_page = 10 }) {
    const q = new URLSearchParams({ project_id, sort, page, per_page });
    return request(`/tasks?${q.toString()}`);
  },
  createTask({ project_id, title, due_date, priority = "normal", status = "todo" }) {
    return request("/tasks", {
      method: "POST",
      body: { project_id, title, due_date, priority, status },
    });
  },
  updateTask(id, patch) {
    return request(`/tasks/${id}`, { method: "PATCH", body: patch });
  },
  deleteTask(id) {
    return request(`/tasks/${id}`, { method: "DELETE" });
  },

  // subtasks
  listSubtasks({ task_id }) {
    const q = new URLSearchParams({ task_id });
    return request(`/subtasks?${q.toString()}`); // expects array
  },
  createSubtask({ task_id, title }) {
    return request("/subtasks", { method: "POST", body: { task_id, title } });
  },
  updateSubtask(id, patch) {
    return request(`/subtasks/${id}`, { method: "PATCH", body: patch });
  },
  deleteSubtask(id) {
    return request(`/subtasks/${id}`, { method: "DELETE" });
  },
};

export default api;