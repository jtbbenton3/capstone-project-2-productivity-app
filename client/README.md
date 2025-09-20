# Productivity App (Capstone Project 2)

Full-stack project with a **Flask** backend and a **Vite/React** frontend.  
Features: signup/login (cookie session), projects, tasks, subtasks, filtering, and pagination.

---

## Tech

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-Migrate, SQLite  
- **Frontend:** Vite + React + react-router-dom  
- **Auth:** Cookie session via Flask-Login (CORS enabled for local dev)  
- **Scripts:** `scripts/smoke_auth.sh`, `scripts/smoke_tasks_subtasks.sh`, `scripts/smoke_full.sh`

---

## Quick Start

### Prereqs
- Python **3.11+** (uses a local `.venv`)
- Node **20+** and npm
- macOS/Linux have `curl` and `jq` by default (used by smoke scripts)

### 1) Backend (dev)

From **repo root**:

    python -m venv .venv
    ./.venv/bin/pip install -r requirements.txt
    ./.venv/bin/python -m flask --app app run -p 5005
    # API: http://127.0.0.1:5005

### 2) Frontend (dev)

From **repo root**:

    cd client
    # Point the frontend to the API (Flask runs on 127.0.0.1:5005)
    printf "VITE_API_BASE=http://127.0.0.1:5005\nAPI_BASE=http://127.0.0.1:5005\n" > .env.local

    npm install
    npm run dev -- --host 127.0.0.1
    # App: http://127.0.0.1:5173

---

## Testing

This repo includes smoke test scripts to quickly verify authentication, projects, tasks, and subtasks.

From **repo root**:

    chmod +x scripts/smoke_full.sh
    API=http://127.0.0.1:5005 ./scripts/smoke_full.sh

---

## Project Features / Usage

### Authentication
- Sign up with username, email, and password (secure cookie session).
- Log in / log out; header reflects current auth state.
- **Protected routes:** `/projects` and project detail pages redirect to Login if not authenticated.

### Projects
- Create, list, and delete projects.

### Tasks (inside a project)
- Create tasks with **title**, **due date**, **status** (`todo`, `in_progress`, `done`), and **priority** (`low`, `normal`, `high`).
- List & paginate tasks; filter by status/priority; sort by due date.
- Update a task’s status/priority, title, or due date inline.
- View task details.

### Subtasks
- Create subtasks for a task.
- Toggle subtask status (done/todo).
- Delete subtasks.

### API Endpoints (used by the frontend)
- **Auth:** `/auth/signup`, `/auth/login`, `/auth/logout`, `/auth/me`
- **Projects:** `/projects`
- **Tasks:** `/tasks`
- **Subtasks:** `/subtasks`

### Verification
- End-to-end smoke scripts:  
  `scripts/smoke_auth.sh`, `scripts/smoke_tasks_subtasks.sh`, `scripts/smoke_full.sh`

---

## Notes

- Frontend expects the API base at `http://127.0.0.1:5005` (configured in `client/.env.local`).
- Update ports/hosts as needed if your local setup differs.