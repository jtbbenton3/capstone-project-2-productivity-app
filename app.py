from __future__ import annotations
import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt

from config import Config

# --- Globals ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Cookies/sessions lifespan
    app.config.setdefault("REMEMBER_COOKIE_DURATION", timedelta(days=14))
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    # Helpful for local dev with curl & a React/Vite dev server
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    # CORS for localhost React/Vite dev server, with cookies
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://127.0.0.1:3000",
                    "http://localhost:3000",
                    "http://127.0.0.1:5173",   # Vite (127.0.0.1)
                    "http://localhost:5173",   # Vite (localhost)
                ]
            }
        },
        supports_credentials=True,
    )

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    
    from models import User, Project, Task, Subtask  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    
    @login_manager.unauthorized_handler
    def _unauthorized():
        return jsonify(error="unauthorized"), 401

    login_manager.login_view = "auth.login"

    # Health check (used by rubric/smoke)
    @app.get("/health")
    def health():
        return {"status": "ok", "user_authenticated": current_user.is_authenticated}, 200

    # JSON error handlers (consistent error payloads)
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="bad request"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error="unauthorized"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error="forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="method not allowed"), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="server error"), 500

    # Create tables if they don't exist 
    with app.app_context():
        db.create_all()

    # Register blueprints
    from auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.subtasks import subtasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(subtasks_bp)

    return app



app = create_app()