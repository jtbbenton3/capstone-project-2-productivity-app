from datetime import date
from flask import Blueprint, request
from flask_login import login_required, current_user
from app import db
from models import Task, Project, STATUS_VALUES
from utils.pagination import parse_pagination_args, paginate_query, task_to_dict

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.get("")
@login_required
def list_tasks():
    """
    List tasks for the current user with pagination.
    Supports both paginate_query return shapes:
      - dict: {"data": [...], "meta": {...}}
      - tuple: (data, meta)
    """
    page, per_page = parse_pagination_args(request)

    q = (
        db.session.query(Task)
        .filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
    )

    result = paginate_query(q, page, per_page)

    # Normalize result into (data, meta)
    if isinstance(result, dict):
        data = result.get("data", [])
        meta = result.get("meta", {})
    elif isinstance(result, tuple) and len(result) == 2:
        data, meta = result
    else:
        # Fallback: assume it's an iterable of rows with no meta
        data = list(result) if result is not None else []
        meta = {"page": page, "per_page": per_page, "total": len(data), "pages": 1}

    # Ensure each item is a dict
    if data and not isinstance(data[0], dict):
        data = [task_to_dict(t) for t in data]

    return {"data": data, "meta": meta}, 200


@tasks_bp.post("")
@login_required
def create_task():
    """
    Create a task under a project owned by the current user.
    Accepts optional: due_date (YYYY-MM-DD), priority (string), status (todo|in_progress|done).
    """
    payload = request.get_json() or {}

    title = (payload.get("title") or "").strip()
    project_id = payload.get("project_id")
    status = (payload.get("status") or "todo").strip()
    priority = (payload.get("priority") or "normal").strip()
    due_date_raw = payload.get("due_date")  # optional "YYYY-MM-DD"

    if not title or not project_id:
        return {"error": "title and project_id are required"}, 400

    # Verify the project exists and belongs to the current user
    try:
        project_id_int = int(project_id)
    except (TypeError, ValueError):
        return {"error": "project_id must be an integer"}, 400

    project = db.session.get(Project, project_id_int)
    if not project or project.user_id != current_user.id:
        return {"error": "project not found or not owned by user"}, 404

    if status not in STATUS_VALUES:
        return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400

    # Parse optional due_date
    parsed_due = None
    if due_date_raw:
        try:
            y, m, d = [int(x) for x in due_date_raw.split("-")]
            parsed_due = date(y, m, d)
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

    # task_to_dict ensures consistent shape with list endpoint
    dto = task_to_dict(t)
    if "created_at" not in dto and getattr(t, "created_at", None):
        dto["created_at"] = t.created_at.isoformat()

    return dto, 201