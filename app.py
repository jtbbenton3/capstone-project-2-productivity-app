# app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, login_manager, bcrypt
from auth import bp as auth_bp
from routes.projects import bp as projects_bp
from routes.tasks import bp as tasks_bp
from routes.subtasks import bp as subtasks_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")

    db_url = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = (db_url or "sqlite:///app.db").replace(
        "postgres://", "postgresql://", 1
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # cookies/CORS for local dev + tests
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    origins = [f"http://127.0.0.1:{p}" for p in (5173, 5174, 5175, 5176, 5177)] + \
              [f"http://localhost:{p}" for p in (5173, 5174, 5175, 5176, 5177)]
    CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # return JSON 401 (no redirects/HTML)
    @login_manager.unauthorized_handler
    def _unauth():
        return jsonify(error="Unauthorized"), 401

    # **critical**: ensure tables match models (sidestep busted Alembic state)
    with app.app_context():
        db.create_all()

    
    Migrate(app, db)

    # routes
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(subtasks_bp, url_prefix="/subtasks")

    @app.get("/health")
    def health():
        return jsonify(ok=True), 200

    return app

app = create_app()