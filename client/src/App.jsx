// client/src/App.jsx
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import Projects from "./pages/Projects.jsx";
import { AuthProvider, useAuth } from "./auth.jsx";
import "./App.css";

function Header() {
  const { me, logout } = useAuth();
  return (
    <header style={{ padding: "12px 16px", borderBottom: "1px solid #333" }}>
      <nav style={{ display: "flex", gap: 16, alignItems: "center" }}>
        <Link to="/">Home</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/login">Login</Link>
        <Link to="/signup">Signup</Link>
        <span style={{ marginLeft: "auto", opacity: 0.85 }}>
          {me ? (
            <>
              Signed in as <strong>{me.username}</strong>{" "}
              <button onClick={logout} style={{ marginLeft: 8 }}>Logout</button>
            </>
          ) : (
            "Not signed in"
          )}
        </span>
      </nav>
    </header>
  );
}

function RequireAuth({ children }) {
  const { me, loading } = useAuth();
  if (loading) return <main style={{ padding: 24 }}>Loading…</main>;
  if (!me) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/projects"
            element={
              <RequireAuth>
                <Projects />
              </RequireAuth>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}