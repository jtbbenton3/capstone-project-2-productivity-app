// client/src/auth.jsx
import { createContext, useContext, useEffect, useState } from "react";
import * as api from "./api";
import { Navigate } from "react-router-dom";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setError("");
      const res = await api.auth.me();
      setUser(res.authenticated ? res.user : null);
    } catch (e) {
      setUser(null);
      setError(e.message || "Failed to refresh session");
    }
  }

  async function login(email, password) {
    setError("");
    await api.auth.login(email, password);
    await refresh();
  }

  async function signup(username, email, password) {
    setError("");
    await api.auth.signup(username, email, password);
    await refresh();
  }

  async function logout() {
    setError("");
    await api.auth.logout();
    setUser(null);
  }

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        await refresh();
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const value = { user, loading, error, refresh, login, signup, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}

export function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <main style={{ padding: 24 }}>Loading…</main>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export const Protected = RequireAuth;