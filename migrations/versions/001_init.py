# migrations/versions/0001_init.py
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_projects_owner_id_created_at", "projects", ["owner_id", "created_at"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="todo"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_project_created_at", "tasks", ["project_id", "created_at"])

    op.create_table(
        "subtasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="todo"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_subtasks_task_created_at", "subtasks", ["task_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_subtasks_task_created_at", table_name="subtasks")
    op.drop_table("subtasks")
    op.drop_index("ix_tasks_project_created_at", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_projects_owner_id_created_at", table_name="projects")
    op.drop_table("projects")
    op.drop_table("users")
    