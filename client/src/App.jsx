import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth, RequireAuth } from "./auth";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import "./App.css";

// header shows session + logout
function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function onLogout() {
    try {
      await logout();
      navigate("/login");
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <header className="topbar">
      <nav className="nav">
        <Link to="/">Home</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/login">Login</Link>
        <Link to="/signup">Signup</Link>
        <span className="spacer" />
        <span>{user ? <>Signed in as <b>{user.username}</b></> : "Not signed in"}</span>
        {user && (
          <button className="btn" onClick={onLogout} style={{ marginLeft: 12 }}>
            Logout
          </button>
        )}
      </nav>
      <hr />
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
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route
            path="/projects"
            element={
              <RequireAuth>
                <Projects />
              </RequireAuth>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <RequireAuth>
                <ProjectDetail />
              </RequireAuth>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}