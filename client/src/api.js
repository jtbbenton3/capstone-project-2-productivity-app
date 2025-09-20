const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5005";

async function request(path, method = "GET", body, headers = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...headers },
    credentials: "include", // send cookies
    body: body ? JSON.stringify(body) : undefined,
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

// auth
export const me = () => request("/auth/me");
export const signup = (username, email, password) =>
  request("/auth/signup", "POST", { username, email, password });
export const login = (email, password) =>
  request("/auth/login", "POST", { email, password });
export const logout = () => request("/auth/logout", "POST");

// example backend call
export const createProject = (title, description) =>
  request("/projects", "POST", { title, description });