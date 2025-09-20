import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import api from "../api";

// list projects and create new ones
export default function Projects() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [title, setTitle] = useState("My Project");
  const [description, setDescription] = useState("Created from UI");
  const [error, setError] = useState("");

  async function load() {
    const res = await api.listProjects();
    
    const arr = Array.isArray(res) ? res : res?.data || [];
    setProjects(arr);
  }

  useEffect(() => {
    (async () => {
      try {
        await load();
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function onCreate(e) {
    e.preventDefault();
    setError("");
    try {
      const created = await api.createProject({ title, description });
      setProjects((prev) => [created, ...prev]);
      setTitle("");
      setDescription("");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <main className="page">
      <h1>Projects</h1>
      <p>Signed in as <b>{user?.username}</b></p>

      <section>
        <h2>Create a project</h2>
        <form onSubmit={onCreate} className="form">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="description" />
          <button className="btn" type="submit">Create project</button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Your projects</h2>
        {loading ? (
          <div>Loading…</div>
        ) : projects.length === 0 ? (
          <div>No projects yet.</div>
        ) : (
          <ul className="list">
            {projects.map((p) => (
              <li key={p.id} className="item">
                <Link to={`/projects/${p.id}`}>{p.title}</Link>
                <span className="muted"> &nbsp; #{p.id}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}