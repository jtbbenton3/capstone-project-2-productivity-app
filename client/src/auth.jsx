import { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

// simple auth context for user + helpers
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);       // null means not logged in
  const [loading, setLoading] = useState(true); // initial load

  async function refreshMe() {
    const me = await api.me();
    setUser(me.authenticated ? me.user : null);
  }

  // load current session once on mount
  useEffect(() => {
    (async () => {
      try {
        await refreshMe();
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // wrappers are convenient for pages
  async function signup({ username, email, password }) {
    await api.signup({ username, email, password });
    await refreshMe();
  }
  async function login(email, password) {
    await api.login(email, password);
    await refreshMe();
  }
  async function logout() {
    await api.logout();
    await refreshMe();
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, refreshMe, signup, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

// gate for routes that need auth
export function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <main style={{ padding: 24 }}>Loading…</main>;
  if (!user) return <main style={{ padding: 24 }}>Please log in.</main>;
  return children;
}