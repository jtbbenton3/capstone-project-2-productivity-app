# routes/projects.py
from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from math import ceil

from app import db
from models import Project, Task, Subtask

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


def _project_to_dict(p: Project):
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
    }


@projects_bp.get("")
@login_required
def list_projects():
    """
    GET /projects
    ?page=&per_page=&q=
    """
    try:
        page = int(request.args.get("page", 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except Exception:
        per_page = 10
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    q = (request.args.get("q") or "").strip()

    qry = db.session.query(Project).filter(Project.user_id == current_user.id)

    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(Project.title.ilike(like), Project.description.ilike(like)))

    # Sort newest first if possible
    if hasattr(Project, "created_at"):
        qry = qry.order_by(Project.created_at.desc())
    else:
        qry = qry.order_by(Project.id.desc())

    total = qry.count()
    items = qry.offset((page - 1) * per_page).limit(per_page).all()
    data = [_project_to_dict(p) for p in items]
    pages = max(1, ceil(total / per_page)) if per_page else 1

    return {"data": data, "meta": {"page": page, "pages": pages, "per_page": per_page, "total": total}}, 200


@projects_bp.post("")
@login_required
def create_project():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title:
        return {"error": "title is required"}, 400

    p = Project(title=title, description=description, user_id=current_user.id)
    db.session.add(p)
    db.session.commit()
    return _project_to_dict(p), 201


@projects_bp.patch("/<int:project_id>")
@login_required
def update_project(project_id: int):
    p = db.session.get(Project, project_id)
    if not p or p.user_id != current_user.id:
        return {"error": "project not found"}, 404

    data = request.get_json() or {}

    if "title" in data:
        new_title = (data.get("title") or "").strip()
        if not new_title:
            return {"error": "title cannot be empty"}, 400
        p.title = new_title

    if "description" in data:
        p.description = (data.get("description") or "").strip()

    db.session.commit()
    return _project_to_dict(p), 200


@projects_bp.delete("/<int:project_id>")
@login_required
def delete_project(project_id: int):
    p = db.session.get(Project, project_id)
    if not p or p.user_id != current_user.id:
        return {"error": "project not found"}, 404

    # Defensive cascade: delete tasks and their subtasks
    tasks = db.session.query(Task).filter_by(project_id=p.id).all()
    for t in tasks:
        subs = db.session.query(Subtask).filter_by(task_id=t.id).all()
        for s in subs:
            db.session.delete(s)
        db.session.delete(t)

    db.session.delete(p)
    db.session.commit()
    return {"deleted": True, "id": project_id}, 200