# auth.py
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User

bp = Blueprint("auth", __name__)

@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify(error="username, email, and password are required"), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(error="username or email already in use"), 400

    u = User(username=username, email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    login_user(u)
    return jsonify(user=u.to_dict()), 201

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400

    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify(error="invalid credentials"), 401

    login_user(u)
    return jsonify(user=u.to_dict()), 200

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return ("", 204)

@bp.get("/me")
def me():
    if current_user.is_authenticated:
        return jsonify(authenticated=True, user=current_user.to_dict()), 200
    return jsonify(authenticated=False), 200