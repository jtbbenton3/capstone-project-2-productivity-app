# app.py
from __future__ import annotations

import os
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# ---- extensions 
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__)

    # ---- config 
    
    app.config.from_object("config.Config")

    # ---- init extensions 
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # ---- CORS  
    CORS(
        app,
        origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        supports_credentials=True,
    )

    # ---- login manager 
    from models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    login_manager.login_view = None  

    # ---- blueprints 
    from auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.subtasks import subtasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(subtasks_bp)

    # ---- health check 
    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}, 200

    # ---- optional root 
    @app.get("/")
    def index():
        return {"service": "productivity-api", "ok": True}, 200

    return app



app = create_app()