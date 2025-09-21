// client/src/pages/Projects.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { projects as projectsApi } from "../api";
import { useAuth } from "../auth";

export default function Projects() {
  const { user, refresh, logout } = useAuth();
  const [list, setList] = useState([]);
  const [title, setTitle] = useState("My Project");
  const [description, setDescription] = useState("Created from UI");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function load() {
    setError("");
    try {
      const data = await projectsApi.list();
      setList(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => {
      try {
        await refresh();
      } catch {}
      await load();
    })();
  }, []);

  async function onCreate(e) {
    e.preventDefault();
    setError("");
    try {
      const p = await projectsApi.create(title.trim(), description.trim());
      setList((prev) => [...prev, p]);
      navigate(`/projects/${p.id}`);
    } catch (e) {
      setError(e.message || "Failed to create project");
    }
  }

  return (
    <main className="container">
      <header className="topbar">
        <nav className="nav">
          <Link to="/">Home</Link>
          <Link to="/projects">Projects</Link>
        </nav>
        <div className="authbox">
          <span>
            Signed in as <strong>{user?.username || "…"}</strong>
          </span>
          <button onClick={logout} className="btn">
            Logout
          </button>
        </div>
      </header>

      <h1>Projects</h1>

      <section className="card">
        <h2>Create a project</h2>
        <form onSubmit={onCreate} className="row">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="description"
          />
          <button type="submit" className="btn">
            Create project
          </button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>

      <h2 style={{ marginTop: 24 }}>Your projects</h2>
      {loading ? (
        <div className="muted">Loading…</div>
      ) : (
        <ul className="list">
          {list.map((p) => (
            <li key={p.id} className="list-item">
              <Link to={`/projects/${p.id}`}>#{p.id} — {p.title}</Link>
            </li>
          ))}
          {list.length === 0 && <li className="muted">No projects yet.</li>}
        </ul>
      )}
    </main>
  );
}