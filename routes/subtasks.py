# routes/subtasks.py
from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from models import db, Subtask, Task, Project

bp = Blueprint("subtasks", __name__)

def user_owns_task(task_id: int) -> bool:
    if not task_id:
        return False
    t = Task.query.get(task_id)
    if not t:
        return False
    p = Project.query.get(t.project_id)
    return bool(p and p.owner_id == current_user.id)

def user_owns_subtask(subtask: Subtask) -> bool:
    if not subtask:
        return False
    return user_owns_task(subtask.task_id)

@bp.get("")
@login_required
def list_subtasks():
    task_id = request.args.get("task_id", type=int)
    if not task_id:
        return jsonify(error="task_id is required"), 400
    if not user_owns_task(task_id):
        abort(404)
    items = Subtask.query.filter_by(task_id=task_id).order_by(Subtask.id.asc()).all()
    return jsonify([s.to_dict() for s in items]), 200

@bp.post("")
@login_required
def create_subtask():
    data = request.get_json(silent=True) or {}
    task_id = data.get("task_id")
    title = (data.get("title") or "").strip()
    if not task_id or not title:
        return jsonify(error="task_id and title are required"), 400
    if not user_owns_task(task_id):
        abort(404)
    s = Subtask(task_id=task_id, title=title, status="todo")
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

@bp.patch("/<int:subtask_id>")
@login_required
def update_subtask(subtask_id: int):
    s = Subtask.query.get(subtask_id)
    if not user_owns_subtask(s):
        abort(404)

    data = request.get_json(silent=True) or {}
    if "title" in data:
        s.title = (data.get("title") or "").strip() or s.title
    if "status" in data:
        val = (data.get("status") or "").strip()
        if val in {"todo", "done"}:
            s.status = val
    db.session.commit()
    return jsonify(s.to_dict()), 200

@bp.delete("/<int:subtask_id>")
@login_required
def delete_subtask(subtask_id: int):
    s = Subtask.query.get(subtask_id)
    if not user_owns_subtask(s):
        abort(404)
    db.session.delete(s)
    db.session.commit()
    return ("", 204)