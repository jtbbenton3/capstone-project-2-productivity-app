# routes/subtasks.py
from flask import Blueprint, request
from flask_login import login_required, current_user
from app import db
from models import Subtask, Task, STATUS_VALUES

subtasks_bp = Blueprint("subtasks", __name__, url_prefix="/subtasks")


def _subtask_to_dict(s: Subtask):
    return {
        "id": s.id,
        "title": s.title,
        "status": s.status,
        "task_id": s.task_id,
        "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
    }


def _get_user_task(task_id: int) -> Task | None:
    t = db.session.get(Task, task_id)
    if not t or t.user_id != current_user.id:
        return None
    return t


@subtasks_bp.post("")
@login_required
def create_subtask():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    task_id = data.get("task_id")
    status = (data.get("status") or "todo").strip()

    if not title or not task_id:
        return {"error": "title and task_id are required"}, 400

    try:
        task_id = int(task_id)
    except Exception:
        return {"error": "task_id must be an integer"}, 400

    task = _get_user_task(task_id)
    if not task:
        return {"error": "task not found or not owned by user"}, 404

    if status not in STATUS_VALUES:
        return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400

    s = Subtask(title=title, task_id=task.id, status=status, user_id=current_user.id)
    db.session.add(s)
    db.session.commit()
    return _subtask_to_dict(s), 201


@subtasks_bp.patch("/<int:subtask_id>")
@login_required
def update_subtask(subtask_id: int):
    s = db.session.get(Subtask, subtask_id)
    if not s:
        return {"error": "subtask not found"}, 404

    parent = _get_user_task(s.task_id)
    if not parent:
        return {"error": "subtask not found"}, 404

    data = request.get_json() or {}

    if "title" in data:
        new_title = (data.get("title") or "").strip()
        if not new_title:
            return {"error": "title cannot be empty"}, 400
        s.title = new_title

    if "status" in data:
        new_status = (data.get("status") or "").strip()
        if new_status not in STATUS_VALUES:
            return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400
        s.status = new_status

    if "task_id" in data:
        new_tid = data.get("task_id")
        if not new_tid:
            return {"error": "task_id cannot be empty"}, 400
        try:
            new_tid = int(new_tid)
        except Exception:
            return {"error": "task_id must be an integer"}, 400

        new_parent = _get_user_task(new_tid)
        if not new_parent:
            return {"error": "target task not found or not owned by user"}, 404
        s.task_id = new_parent.id

    db.session.commit()
    return _subtask_to_dict(s), 200


@subtasks_bp.get("")
@login_required
def list_subtasks():
    """
    GET /subtasks
    Optional:
      - task_id
      - status
    """
    q = (
        db.session.query(Subtask)
        .join(Task, Task.id == Subtask.task_id)
        .filter(Task.user_id == current_user.id)
    )

    task_id_raw = request.args.get("task_id")
    if task_id_raw:
        try:
            tid = int(task_id_raw)
        except Exception:
            return {"error": "task_id must be an integer"}, 400
        if not _get_user_task(tid):
            return {"error": "task not found or not owned by user"}, 404
        q = q.filter(Subtask.task_id == tid)

    status = request.args.get("status")
    if status:
        if status not in STATUS_VALUES:
            return {"error": f"status must be one of {list(STATUS_VALUES)}"}, 400
        q = q.filter(Subtask.status == status)

    subs = q.order_by(Subtask.id.asc()).all()
    return [_subtask_to_dict(s) for s in subs], 200


@subtasks_bp.delete("/<int:subtask_id>")
@login_required
def delete_subtask(subtask_id: int):
    s = db.session.get(Subtask, subtask_id)
    if not s:
        return {"error": "subtask not found"}, 404

    parent = _get_user_task(s.task_id)
    if not parent:
        return {"error": "subtask not found"}, 404

    db.session.delete(s)
    db.session.commit()
    return {"deleted": True, "id": subtask_id}, 200