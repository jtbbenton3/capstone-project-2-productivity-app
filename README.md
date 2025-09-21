# 📚 Daily Student Productivity – Capstone Project 2

A full-stack productivity application designed for students to **organize projects, tasks, and subtasks**, track progress with filters and pagination, and manage daily workloads effectively.  

This project was built as part of **Flatiron School – Software Engineering (Capstone Project 2)**.

---

## 🚀 Features

- **Authentication**
  - Secure signup, login, logout with session cookies.
  - Route protection for authenticated users only.

- **Projects**
  - Create, list, view, and delete projects.
  - Ownership rules: users can only manage their own projects.

- **Tasks**
  - Create, update, delete tasks within projects.
  - Pagination & filtering by status (`todo`, `in_progress`, `done`).
  - Priority & due date fields.

- **Subtasks**
  - Nested under tasks.
  - Create, toggle completion, delete.

- **Frontend**
  - Built with **React + Vite**.
  - Environment-based API config (`.env.local`).
  - Clean UI for managing projects, tasks, and subtasks.

- **Backend**
  - Built with **Flask + SQLAlchemy**.
  - SQLite (default) with easy switch to PostgreSQL.
  - Organized with Blueprints (`auth`, `projects`, `tasks`, `subtasks`).
  - Alembic for migrations.

- **Testing**
  - Full **end-to-end (E2E)** test suite (`scripts/run_e2e.sh` + `scripts/e2e_test.py`).
  - Covers signup → project → task → subtask → logout flow.
  - ✅ 48/48 tests passing.

---

## 🛠️ Tech Stack

- **Frontend**: React, Vite, JavaScript
- **Backend**: Python, Flask, SQLAlchemy, Alembic
- **Database**: SQLite (dev), PostgreSQL (optional)
- **Testing**: Python `requests`, custom E2E test scripts

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone <YOUR_REPO_URL>
cd Capstone-Project-2-server
```

### 2. Backend setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate


# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend setup
```bash
cd client
printf "VITE_API_BASE=http://127.0.0.1:5005\n" > .env.local
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### 4. Running Tests

From the backend root (`Capstone-Project-2-server`):

```bash
# Option 1: Bash runner
BASE_URL=http://127.0.0.1:5005 FRONTEND_URL=http://127.0.0.1:5173 ./scripts/run_e2e.sh

# Option 2: Python runner
python scripts/e2e_test.py --base http://127.0.0.1:5005 --frontend http://127.0.0.1:5173
```

### 5. Running the App

#### Start the Backend
From the backend root (`Capstone-Project-2-server`):

```bash
source .venv/bin/activate
flask run --port 5005
```

This will start the API server at:
➡️ http://127.0.0.1:5005

### Start the Frontend

From the client folder:

npm run dev -- --host 127.0.0.1 --port 5173

This will start the React frontend at:
➡️ http://127.0.0.1:5173

You should now be able to sign up, create projects, tasks, and subtasks directly in the web app.