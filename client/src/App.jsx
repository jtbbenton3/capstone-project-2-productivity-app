// client/src/App.jsx
import "./App.css";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { AuthProvider, useAuth, RequireAuth } from "./auth";

import Home from "./pages/Home";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="topbar">
      <nav className="nav">
        <Link to="/">Home</Link>
        <Link to="/projects">Projects</Link>
        {!user && <Link to="/login">Login</Link>}
        {!user && <Link to="/signup">Signup</Link>}
      </nav>
      <div className="authbox">
        {user ? <span>Signed in as <strong>{user.username}</strong></span> : <span>Not signed in</span>}
        {user && <button onClick={logout} className="btn">Logout</button>}
      </div>
    </header>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
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
          <Route
            path="/projects/:projectId"
            element={
              <RequireAuth>
                <ProjectDetail />
              </RequireAuth>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}