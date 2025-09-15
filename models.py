from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt

# ----- Constants -----
STATUS_VALUES = ("todo", "in_progress", "done")

# ----- Models -----
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", backref="owner", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="owner", lazy=True, cascade="all, delete-orphan")
    subtasks = db.relationship("Subtask", backref="owner", lazy=True, cascade="all, delete-orphan")

    # auth helpers
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default="normal")  # simple string for now
    status = db.Column(db.Enum(*STATUS_VALUES, name="status_enum"), nullable=False, default="todo")
    notes = db.Column(db.Text, default="")
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    subtasks = db.relationship("Subtask", backref="task", lazy=True, cascade="all, delete-orphan")


class Subtask(db.Model):
    __tablename__ = "subtasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Enum(*STATUS_VALUES, name="substatus_enum"), nullable=False, default="todo")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)