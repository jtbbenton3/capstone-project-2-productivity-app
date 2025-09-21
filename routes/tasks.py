# routes/tasks.py
from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import asc, desc
from models import db, Task, Project
from utils.pagination import paginate

bp = Blueprint("tasks", __name__)

VALID_STATUS = {"todo", "in_progress", "done"}
VALID_PRIORITY = {"low", "normal", "high"}
VALID_SORT = {"created_at", "due_date", "priority", "status", "title"}

def user_owns_project(project_id: int) -> bool:
    if not project_id:
        return False
    p = Project.query.get(project_id)
    return bool(p and p.owner_id == current_user.id)

def task_visible_to_user(task: Task) -> bool:
    if not task:
        return False
    p = Project.query.get(task.project_id)
    return bool(p and p.owner_id == current_user.id)

@bp.get("")
@login_required
def list_tasks():
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify(error="project_id is required"), 400
    if not user_owns_project(project_id):
        abort(404)

    page = max(1, request.args.get("page", default=1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", default=10, type=int)))
    status = (request.args.get("status") or "all").strip()
    sort = (request.args.get("sort") or "due_date").strip()
    if sort not in VALID_SORT:
        sort = "due_date"

    q = Task.query.filter_by(project_id=project_id)
    if status != "all":
        if status not in VALID_STATUS:
            return jsonify(error="invalid status"), 400
        q = q.filter(Task.status == status)

    sort_col = getattr(Task, sort)
    # default ascending for due_date; created_at newest first is also fine — keep asc for consistency
    q = q.order_by(asc(sort_col))
    return jsonify(paginate(q, page=page, per_page=per_page, serializer=lambda t: t.to_dict())), 200

@bp.post("")
@login_required
def create_task():
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    title = (data.get("title") or "").strip()
    due_date = (data.get("due_date") or None)
    priority = (data.get("priority") or "normal").strip()
    status = (data.get("status") or "todo").strip()

    if not project_id or not title:
        return jsonify(error="project_id and title are required"), 400
    if not user_owns_project(project_id):
        abort(404)
    if priority not in VALID_PRIORITY:
        return jsonify(error="invalid priority"), 400
    if status not in VALID_STATUS:
        return jsonify(error="invalid status"), 400

    t = Task(project_id=project_id, title=title, priority=priority, status=status)
    if due_date:
        t.due_date = due_date  # ISO yyyy-mm-dd string works with SQLite adapter
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

@bp.patch("/<int:task_id>")
@login_required
def update_task(task_id: int):
    t = Task.query.get(task_id)
    if not task_visible_to_user(t):
        abort(404)

    data = request.get_json(silent=True) or {}
    if "title" in data:
        t.title = (data.get("title") or "").strip() or t.title
    if "due_date" in data:
        t.due_date = data.get("due_date") or None
    if "priority" in data:
        val = (data.get("priority") or "").strip()
        if val and val in VALID_PRIORITY:
            t.priority = val
    if "status" in data:
        val = (data.get("status") or "").strip()
        if val and val in VALID_STATUS:
            t.status = val

    db.session.commit()
    return jsonify(t.to_dict()), 200

@bp.delete("/<int:task_id>")
@login_required
def delete_task(task_id: int):
    t = Task.query.get(task_id)
    if not task_visible_to_user(t):
        abort(404)
    db.session.delete(t)
    db.session.commit()
    return ("", 204)