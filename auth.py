from flask import Blueprint, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/signup")
def signup():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return {"error": "username, email, and password are required"}, 400

    # checks
    if db.session.query(User).filter((User.username == username) | (User.email == email)).first():
        return {"error": "username or email already exists"}, 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)  # start the session
    return {"id": user.id, "username": user.username, "email": user.email}, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return {"error": "email and password are required"}, 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {"error": "invalid credentials"}, 400

    login_user(user)
    return {"id": user.id, "username": user.username, "email": user.email}, 200


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return {"message": "logged out"}, 200


@auth_bp.get("/me")
def me():
    if not current_user.is_authenticated:
        return {"authenticated": False, "user": None}, 200
    return {
        "authenticated": True,
        "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email}
    }, 200