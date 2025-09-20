import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { projects } from "../api";
import { useAuth } from "../auth";

// very small page: create a project and list your projects
export default function Projects() {
  const { user, refreshMe, logout } = useAuth();
  const [list, setList] = useState([]);
  const [title, setTitle] = useState("My Project");
  const [description, setDescription] = useState("Created from UI");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        await refreshMe();
        const data = await projects.list();
        setList(data || []);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [refreshMe]);

  async function onCreate(e) {
    e.preventDefault();
    setError("");
    try {
      const p = await projects.create(title.trim(), description.trim());
      setList((prev) => [...prev, p]);
      // jump straight into the new project
      navigate(`/projects/${p.id}`);
    } catch (e) {
      setError(e.message);
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
          <span>Signed in as <strong>{user?.username || "…"}</strong></span>
          <button onClick={logout} className="btn">Logout</button>
        </div>
      </header>

      <h1>Projects</h1>
      <p>Signed in as <strong>{user?.username}</strong></p>

      <section className="card">
        <h2>Create a project</h2>
        <form onSubmit={onCreate} className="row">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="description" />
          <button type="submit" className="btn">Create project</button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>

      <h2 style={{ marginTop: 24 }}>Your projects</h2>
      <ul className="list">
        {list.map((p) => (
          <li key={p.id} className="list-item">
            <Link to={`/projects/${p.id}`}>#{p.id} — {p.title}</Link>
          </li>
        ))}
        {list.length === 0 && <li className="muted">No projects yet.</li>}
      </ul>
    </main>
  );
}