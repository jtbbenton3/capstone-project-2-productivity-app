# routes/projects.py
from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from models import db, Project

bp = Blueprint("projects", __name__)

def require_owner(project: Project):
    if not project or project.owner_id != current_user.id:
        abort(404)

@bp.get("")
@login_required
def list_projects():
    items = Project.query.filter_by(owner_id=current_user.id).order_by(Project.id.asc()).all()
    return jsonify([p.to_dict() for p in items]), 200

@bp.post("")
@login_required
def create_project():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    p = Project(owner_id=current_user.id, title=title, description=description)
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@bp.get("/<int:project_id>")
@login_required
def get_project(project_id: int):
    p = Project.query.get(project_id)
    require_owner(p)
    return jsonify(p.to_dict()), 200

@bp.delete("/<int:project_id>")
@login_required
def delete_project(project_id: int):
    p = Project.query.get(project_id)
    require_owner(p)
    db.session.delete(p)
    db.session.commit()
    return ("", 204)