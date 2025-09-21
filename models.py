# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    projects = db.relationship("Project", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw: str):
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default="", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description}

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(20), default="todo", nullable=False)       # todo | in_progress | done
    priority = db.Column(db.String(20), default="normal", nullable=False)   # low | normal | high
    due_date = db.Column(db.String(10), nullable=True)  # store as 'YYYY-MM-DD' for simplicity
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    subtasks = db.relationship("Subtask", backref="task", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

class Subtask(db.Model):
    __tablename__ = "subtasks"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(20), default="todo", nullable=False)  # todo | done
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
        }