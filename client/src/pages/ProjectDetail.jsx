import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

// shows tasks for one project and lets you manage subtasks
export default function ProjectDetail() {
  const { id } = useParams(); // project id
  const projectId = useMemo(() => Number(id), [id]);

  const [tasks, setTasks] = useState([]);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);

  // new task form
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [priority, setPriority] = useState("normal");
  const [status, setStatus] = useState("todo");
  const [error, setError] = useState("");

  async function loadTasks() {
    const res = await api.listTasks({ project_id: projectId, sort: "due_date" });
    // backend returns {data:[...], meta:{...}}
    setTasks(res.data || []);
    setMeta(res.meta || null);
  }

  useEffect(() => {
    (async () => {
      try {
        await loadTasks();
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId]);

  async function onCreateTask(e) {
    e.preventDefault();
    setError("");
    try {
      const created = await api.createTask({
        project_id: projectId,
        title,
        due_date: due || null,
        priority,
        status,
      });
      setTasks((cur) => [created, ...cur]);
      setTitle("");
      setDue("");
      setPriority("normal");
      setStatus("todo");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <main className="page">
      <h1>Project #{projectId}</h1>

      <section>
        <h2>Create a task</h2>
        <form className="form grid" onSubmit={onCreateTask}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
          <input value={due} onChange={(e) => setDue(e.target.value)} type="date" />
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
          <button className="btn" type="submit">Create task</button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Tasks</h2>
        {loading ? (
          <div>Loading…</div>
        ) : tasks.length === 0 ? (
          <div>No tasks yet.</div>
        ) : (
          <div className="cards">
            {tasks.map((t) => (
              <TaskCard key={t.id} task={t} />
            ))}
          </div>
        )}
        {meta && (
          <div className="muted" style={{ marginTop: 8 }}>
            page {meta.page} of {meta.pages} • total {meta.total}
          </div>
        )}
      </section>
    </main>
  );
}

// small component for a single task + subtasks
function TaskCard({ task }) {
  const [subtasks, setSubtasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [err, setErr] = useState("");

  async function load() {
    const arr = await api.listSubtasks({ task_id: task.id });
    setSubtasks(Array.isArray(arr) ? arr : arr?.data || []);
  }

  useEffect(() => {
    (async () => {
      try {
        await load();
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [task.id]);

  async function onAdd(e) {
    e.preventDefault();
    setErr("");
    try {
      const created = await api.createSubtask({ task_id: task.id, title });
      setSubtasks((cur) => [...cur, created]);
      setTitle("");
    } catch (e) {
      setErr(e.message);
    }
  }

  async function onToggleStatus(st) {
    // simple toggle: todo -> in_progress -> done -> todo
    const next =
      st.status === "todo" ? "in_progress" : st.status === "in_progress" ? "done" : "todo";
    const updated = await api.updateSubtask(st.id, { status: next });
    setSubtasks((cur) => cur.map((x) => (x.id === st.id ? updated : x)));
  }

  async function onDelete(st) {
    await api.deleteSubtask(st.id);
    setSubtasks((cur) => cur.filter((x) => x.id !== st.id));
  }

  return (
    <article className="card">
      <header className="card-head">
        <div><b>{task.title}</b></div>
        <div className="muted">
          due {task.due_date || "—"} • {task.priority} • {task.status}
        </div>
      </header>

      <div style={{ marginTop: 8 }}>
        <form onSubmit={onAdd} className="form">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="new subtask" />
          <button className="btn" type="submit">Add</button>
        </form>
        {err && <div className="error">{err}</div>}
      </div>

      <ul className="list" style={{ marginTop: 12 }}>
        {loading ? (
          <li>Loading subtasks…</li>
        ) : subtasks.length === 0 ? (
          <li className="muted">No subtasks.</li>
        ) : (
          subtasks.map((st) => (
            <li key={st.id} className="item">
              <span>
                [{st.status}] {st.title}
              </span>
              <span>
                <button className="btn small" onClick={() => onToggleStatus(st)}>
                  Next status
                </button>
                <button className="btn small danger" onClick={() => onDelete(st)}>
                  Delete
                </button>
              </span>
            </li>
          ))
        )}
      </ul>
    </article>
  );
}