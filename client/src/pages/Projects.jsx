// client/src/pages/Projects.jsx
import { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../auth";

export default function Projects() {
  const { me } = useAuth();
  const [project, setProject] = useState(null);
  const [projTitle, setProjTitle] = useState("My Project");
  const [projDesc, setProjDesc] = useState("Created from UI");

  // task form
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [priority, setPriority] = useState("normal");
  const [status, setStatus] = useState("todo");

  // task list
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");

  async function refreshTasks(pid) {
    if (!pid) return;
    try {
      const out = await api.listTasks({ project_id: pid, sort: "due_date" });
      setTasks(out.data || []);
    } catch (err) {
      setError(err.message || "Failed to load tasks");
    }
  }

  async function createProject(e) {
    e?.preventDefault();
    setError("");
    try {
      const p = await api.createProject({ title: projTitle.trim(), description: projDesc.trim() });
      setProject(p);
      await refreshTasks(p.id);
    } catch (err) {
      setError(err.message || "Failed to create project");
    }
  }

  async function addTask(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createTask({
        project_id: project.id,
        title: title.trim(),
        due_date: due || null,
        priority,
        status,
      });
      setTitle("");
      setDue("");
      setPriority("normal");
      setStatus("todo");
      await refreshTasks(project.id);
    } catch (err) {
      setError(err.message || "Failed to create task");
    }
  }

  // No auto-create: user chooses when to create a project
  useEffect(() => {
    setTasks([]);
  }, []);

  return (
    <main style={{ padding: 24 }}>
      <h2>Projects</h2>
      <div style={{ marginBottom: 12 }}>
        {me ? `Signed in as ${me.username}` : "Not signed in"}
      </div>

      {error && <div style={{ color: "crimson", marginBottom: 12 }}>{error}</div>}

      {!project ? (
        <section style={{ marginBottom: 24 }}>
          <h3>Create a project</h3>
          <form onSubmit={createProject} style={{ display: "grid", gap: 8, maxWidth: 420 }}>
            <input value={projTitle} onChange={(e) => setProjTitle(e.target.value)} placeholder="title" />
            <input value={projDesc} onChange={(e) => setProjDesc(e.target.value)} placeholder="description" />
            <button type="submit">Create project</button>
          </form>
        </section>
      ) : (
        <>
          <section style={{ marginBottom: 24 }}>
            <h3>Project</h3>
            <div><strong>{project.title}</strong></div>
            <div style={{ opacity: 0.8 }}>{project.description}</div>
            <div style={{ opacity: 0.8 }}>ID: {project.id}</div>
          </section>

          <section style={{ marginBottom: 24 }}>
            <h3>Add task</h3>
            <form onSubmit={addTask} style={{ display: "grid", gap: 8, maxWidth: 520 }}>
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
              <input type="date" value={due} onChange={(e) => setDue(e.target.value)} />
              <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                <option value="low">low</option>
                <option value="normal">normal</option>
                <option value="high">high</option>
              </select>
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="todo">todo</option>
                <option value="in_progress">in_progress</option>
                <option value="done">done</option>
              </select>
              <button type="submit">Create task</button>
            </form>
          </section>

          <section>
            <h3>Tasks</h3>
            {tasks.length === 0 ? (
              <div>No tasks yet.</div>
            ) : (
              <table style={{ borderCollapse: "collapse", width: "100%", maxWidth: 720 }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: "left", borderBottom: "1px solid #333", padding: 6 }}>ID</th>
                    <th style={{ textAlign: "left", borderBottom: "1px solid #333", padding: 6 }}>Title</th>
                    <th style={{ textAlign: "left", borderBottom: "1px solid #333", padding: 6 }}>Status</th>
                    <th style={{ textAlign: "left", borderBottom: "1px solid #333", padding: 6 }}>Priority</th>
                    <th style={{ textAlign: "left", borderBottom: "1px solid #333", padding: 6 }}>Due</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((t) => (
                    <tr key={t.id}>
                      <td style={{ padding: 6 }}>{t.id}</td>
                      <td style={{ padding: 6 }}>{t.title}</td>
                      <td style={{ padding: 6 }}>{t.status}</td>
                      <td style={{ padding: 6 }}>{t.priority}</td>
                      <td style={{ padding: 6 }}>{t.due_date || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </main>
  );
}