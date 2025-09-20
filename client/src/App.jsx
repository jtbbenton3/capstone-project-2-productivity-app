import { useEffect, useState, useCallback } from "react";
import { Link, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import * as api from "./api";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    try {
      const data = await api.me();
      setUser(data?.user || null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  return (
    <>
      <nav style={{ display: "flex", gap: 16, padding: 12 }}>
        <Link to="/">Home</Link>
        <Link to="/login">Login</Link>
        <Link to="/signup">Signup</Link>
        <span style={{ marginLeft: 8 }}>
          {user ? `Signed in as ${user.username}` : "Not signed in"}
        </span>
      </nav>

      <Routes>
        <Route index element={<Home user={user} loading={loading} onRefresh={refreshMe} />} />
        <Route path="login" element={<Login onLoggedIn={refreshMe} />} />
        <Route path="signup" element={<Signup onSignedUp={refreshMe} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}