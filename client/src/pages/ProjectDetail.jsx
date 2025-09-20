import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { tasks, subtasks } from "../api";
import { useAuth } from "../auth";

// simple helpers for display + cycling through states
const STATUSES = ["todo", "in_progress", "done"];
const PRIORITIES = ["low", "normal", "high"];

export default function ProjectDetail() {
  const { id } = useParams(); 
  const projectId = Number(id);
  const { user, refreshMe, logout } = useAuth();

  // create task form
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [priority, setPriority] = useState("high");
  const [status, setStatus] = useState("todo");

  // list controls
  const [filterStatus, setFilterStatus] = useState("all");
  const [perPage, setPerPage] = useState(10);
  const [page, setPage] = useState(1);

  // data + ui state
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [subs, setSubs] = useState({}); // taskId -> subtask list
  const [error, setError] = useState("");

  // load tasks list
  async function load() {
    setError("");
    try {
      const resp = await tasks.list({
        projectId,
        page,
        perPage,
        status: filterStatus,
        sort: "due_date",
      });
      setRows(resp.data);
      setMeta(resp.meta);
      // pre-load subtasks for those on screen
      const all = {};
      for (const t of resp.data) {
        all[t.id] = await subtasks.list(t.id);
      }
      setSubs(all);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    (async () => {
      try {
        await refreshMe();
        await load();
      } catch (e) {
        setError(e.message);
      }
    })();
    
  }, [projectId, page, perPage, filterStatus]);

  async function onCreateTask(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setError("");
    try {
      await tasks.create({
        projectId,
        title: title.trim(),
        dueDate: due || null,
        priority,
        status,
      });
      setTitle("");
      setDue("");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function nextStatus(task) {
    const idx = STATUSES.indexOf(task.status);
    const next = STATUSES[(idx + 1) % STATUSES.length];
    await tasks.update(task.id, { status: next });
    await load();
  }

  async function updatePriority(task, value) {
    await tasks.update(task.id, { priority: value });
    await load();
  }

  async function deleteTask(task) {
    await tasks.remove(task.id);
    await load();
  }

  async function addSubtask(taskId, title) {
    if (!title.trim()) return;
    await subtasks.create({ taskId, title: title.trim() });
    const list = await subtasks.list(taskId);
    setSubs((m) => ({ ...m, [taskId]: list }));
  }

  async function toggleSubtask(st) {
    const next = st.status === "done" ? "todo" : "done";
    await subtasks.update(st.id, { status: next });
    const list = await subtasks.list(st.task_id);
    setSubs((m) => ({ ...m, [st.task_id]: list }));
  }

  async function deleteSubtask(st) {
    await subtasks.remove(st.id);
    const list = await subtasks.list(st.task_id);
    setSubs((m) => ({ ...m, [st.task_id]: list }));
  }

  const canPrev = useMemo(() => meta.page > 1, [meta.page]);
  const canNext = useMemo(() => meta.page < meta.pages, [meta.page, meta.pages]);

  return (
    <main className="container">
      <header className="topbar">
        <nav className="nav">
          <Link to="/">Home</Link>
          <Link to="/projects">Projects</Link>
        </nav>
        <div className="authbox">
          <span>Signed in as <strong>{user?.username}</strong></span>
          <button onClick={logout} className="btn">Logout</button>
        </div>
      </header>

      <h1>Project #{projectId}</h1>

      <section className="card">
        <h2>Create a task</h2>
        <form onSubmit={onCreateTask} className="row wrap">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" />
          <input type="date" value={due} onChange={(e) => setDue(e.target.value)} />
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <button type="submit" className="btn">Create task</button>
        </form>
      </section>

      <section className="row" style={{ alignItems: "center", gap: 16, marginTop: 16 }}>
        <label>status</label>
        <select value={filterStatus} onChange={(e) => { setPage(1); setFilterStatus(e.target.value); }}>
          {["all", ...STATUSES].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>

        <label>per page</label>
        <select value={perPage} onChange={(e) => { setPage(1); setPerPage(Number(e.target.value)); }}>
          {[5, 10, 20].map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </section>

      <h2 style={{ marginTop: 12 }}>Tasks</h2>
      {error && <div className="error">{error}</div>}

      {rows.map((t) => (
        <article key={t.id} className="task">
          <header className="task-head">
            <strong>{t.title}</strong>
            <span className="muted">due {t.due_date || "—"}</span>
          </header>

          <div className="row wrap" style={{ gap: 8, margin: "8px 0" }}>
            <div>
              <label className="muted">status</label>
              <div className="row">
                <select value={t.status} onChange={(e) => tasks.update(t.id, { status: e.target.value }).then(load)}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <button className="btn" onClick={() => nextStatus(t)}>Next status</button>
              </div>
            </div>

            <div>
              <label className="muted">priority</label>
              <select value={t.priority} onChange={(e) => updatePriority(t, e.target.value)}>
                {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <button className="btn danger" onClick={() => deleteTask(t)}>Delete task</button>
          </div>

          <SubtasksBox
            list={subs[t.id] || []}
            onAdd={(title) => addSubtask(t.id, title)}
            onToggle={toggleSubtask}
            onDelete={deleteSubtask}
          />
        </article>
      ))}

      {/* Pagination footer */}
      <footer className="row" style={{ gap: 12, marginTop: 12 }}>
        <span className="muted">page {meta.page} of {meta.pages} • total {meta.total}</span>
        <button className="btn" disabled={!canPrev} onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</button>
        <button className="btn" disabled={!canNext} onClick={() => setPage((p) => p + 1)}>Next</button>
      </footer>
    </main>
  );
}

function SubtasksBox({ list, onAdd, onToggle, onDelete }) {
  const [title, setTitle] = useState("");
  return (
    <div className="card" style={{ marginTop: 8 }}>
      <div className="row" style={{ gap: 8 }}>
        <input
          placeholder="new subtask"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (onAdd(title), setTitle(""))}
        />
        <button className="btn" onClick={() => (onAdd(title), setTitle(""))}>Add</button>
      </div>

      <ul className="list" style={{ marginTop: 8 }}>
        {list.map((s) => (
          <li key={s.id} className="list-item row" style={{ justifyContent: "space-between" }}>
            <span>[{s.status}] {s.title}</span>
            <div className="row" style={{ gap: 8 }}>
              <button className="btn" onClick={() => onToggle(s)}>Toggle</button>
              <button className="btn danger" onClick={() => onDelete(s)}>Delete</button>
            </div>
          </li>
        ))}
        {list.length === 0 && <li className="muted">No subtasks.</li>}
      </ul>
    </div>
  );
}