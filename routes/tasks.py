# routes/tasks.py
from datetime import date
from flask import Blueprint, request
from flask_login import login_required, current_user
from app import db
from models import Task, Project, Subtask, STATUS_VALUES
from utils.pagination import (
    parse_pagination_args,
    paginate_query,
    parse_sort,
    apply_sorts,
)

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def _parse_iso_date_or_none(value):
    if value in (None, "", "null"):
        return None
    y, m, d = [int(x) for x in str(value).split("-")]
    return date(y, m, d)


def _task_to_dict(t: Task):
    return {
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "project_id": t.project_id,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "priority": t.priority,
        "created_at": t.created_at.isoformat() if getattr(t, "created_at", None) else None,
    }


@tasks_bp.get("")
@login_required
def list_tasks():
    """
    GET /tasks
    Filters: status, project_id, due_before, q
    Sorting: ?sort=due_date,-priority,created_at etc.
    Pagination: ?page=&per_page=
    """
    q = (
        db.session.query(Task)
        .filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
    )

    status = request.args.get("status")
    if status:
        if status not in STATUS_VALUES:
            return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400
        q = q.filter(Task.status == status)

    project_id_raw = request.args.get("project_id")
    if project_id_raw:
        try:
            pid = int(project_id_raw)
        except ValueError:
            return {"error": "project_id must be an integer"}, 400
        proj = db.session.get(Project, pid)
        if not proj or proj.user_id != current_user.id:
            return {"error": "project not found or not owned by user"}, 404
        q = q.filter(Task.project_id == pid)

    due_before_raw = request.args.get("due_before")
    if due_before_raw:
        try:
            due_cutoff = _parse_iso_date_or_none(due_before_raw)
            if not due_cutoff:
                return {"error": "due_before must be YYYY-MM-DD"}, 400
        except Exception:
            return {"error": "due_before must be YYYY-MM-DD"}, 400
        q = q.filter(Task.due_date.isnot(None), Task.due_date <= due_cutoff)

    query_text = request.args.get("q")
    if query_text:
        like = f"%{query_text.strip()}%"
        q = q.filter(Task.title.ilike(like))

    sorts = parse_sort(request, default="-created_at")
    q = apply_sorts(q, sorts, default_field=Task.created_at, tie_breaker=Task.id)

    page, per_page = parse_pagination_args(request)
    items, meta = paginate_query(q, page, per_page)

    return {"data": [_task_to_dict(t) for t in items], "meta": meta}, 200


@tasks_bp.get("/<int:task_id>")
@login_required
def get_task(task_id: int):
    t = db.session.get(Task, task_id)
    if not t or t.user_id != current_user.id:
        return {"error": "task not found"}, 404

    subs = (
        db.session.query(Subtask)
        .filter_by(task_id=t.id)
        .order_by(Subtask.id.asc())
        .all()
    )

    task_dict = _task_to_dict(t)
    task_dict["subtasks"] = [
        {
            "id": s.id,
            "title": s.title,
            "status": s.status,
            "task_id": s.task_id,
            "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
        }
        for s in subs
    ]
    return task_dict, 200


@tasks_bp.post("")
@login_required
def create_task():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    project_id = data.get("project_id")
    status = (data.get("status") or "todo").strip()
    priority = (data.get("priority") or "normal").strip()
    due_date_raw = data.get("due_date")

    if not title or not project_id:
        return {"error": "title and project_id are required"}, 400

    project = db.session.get(Project, int(project_id))
    if not project or project.user_id != current_user.id:
        return {"error": "project not found or not owned by user"}, 404

    if status not in STATUS_VALUES:
        return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400

    try:
        parsed_due = _parse_iso_date_or_none(due_date_raw)
    except Exception:
        return {"error": "due_date must be YYYY-MM-DD"}, 400

    t = Task(
        title=title,
        project_id=project.id,
        user_id=current_user.id,
        status=status,
        priority=priority,
        due_date=parsed_due,
    )
    db.session.add(t)
    db.session.commit()

    return _task_to_dict(t), 201


@tasks_bp.patch("/<int:task_id>")
@login_required
def update_task(task_id: int):
    t = db.session.get(Task, task_id)
    if not t or t.user_id != current_user.id:
        return {"error": "task not found"}, 404

    data = request.get_json() or {}

    if "title" in data:
        new_title = (data.get("title") or "").strip()
        if not new_title:
            return {"error": "title cannot be empty"}, 400
        t.title = new_title

    if "status" in data:
        new_status = (data.get("status") or "").strip()
        if new_status not in STATUS_VALUES:
            return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400
        t.status = new_status

    if "priority" in data:
        t.priority = (data.get("priority") or "").strip()

    if "due_date" in data:
        try:
            t.due_date = _parse_iso_date_or_none(data.get("due_date"))
        except Exception:
            return {"error": "due_date must be YYYY-MM-DD or null"}, 400

    if "project_id" in data:
        pid = data.get("project_id")
        if not pid:
            return {"error": "project_id cannot be empty"}, 400
        new_proj = db.session.get(Project, int(pid))
        if not new_proj or new_proj.user_id != current_user.id:
            return {"error": "project not found or not owned by user"}, 404
        t.project_id = new_proj.id

    db.session.commit()
    return _task_to_dict(t), 200


@tasks_bp.delete("/<int:task_id>")
@login_required
def delete_task(task_id: int):
    t = db.session.get(Task, task_id)
    if not t or t.user_id != current_user.id:
        return {"error": "task not found"}, 404

    subs = db.session.query(Subtask).filter_by(task_id=t.id).all()
    for s in subs:
        db.session.delete(s)

    db.session.delete(t)
    db.session.commit()
    return {"deleted": True, "id": task_id}, 200