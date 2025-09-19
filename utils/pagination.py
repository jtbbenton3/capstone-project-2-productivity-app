# utils/pagination.py
from __future__ import annotations
import math
from typing import Tuple, List, Dict, Any, Union
from flask import Request
from sqlalchemy import asc, desc, nullslast

from models import Project, Task, Subtask

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


def parse_pagination_args(request: Request) -> Tuple[int, int]:
    """Parse ?page=&per_page= query params with sane defaults/limits."""
    try:
        page = int(request.args.get("page", DEFAULT_PAGE))
    except Exception:
        page = DEFAULT_PAGE

    try:
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
    except Exception:
        per_page = DEFAULT_PER_PAGE

    page = max(1, page)
    per_page = max(1, min(MAX_PER_PAGE, per_page))
    return page, per_page


# ---------- Sorting helpers ----------
def parse_sort(arg: Union[str, Request, None], default: str = "-created_at") -> List[Tuple[str, str]]:
    """
    Accept either:
      - a Flask Request (reads ?sort=... from query string), or
      - a raw sort string like "-due_date,priority", or
      - None.

    Returns a list of (field, direction) where direction is 'asc' or 'desc'.
    """
    if hasattr(arg, "args"):  # Request-like
        sort_param = (arg.args.get("sort") or "").strip()  # type: ignore[attr-defined]
    else:
        sort_param = (arg or "").strip()

    if not sort_param:
        sort_param = (default or "").strip()

    if not sort_param:
        return []

    parts = [p.strip() for p in sort_param.split(",") if p.strip()]
    out: List[Tuple[str, str]] = []
    for p in parts:
        direction = "asc"
        field = p
        if p.startswith("-"):
            direction = "desc"
            field = p[1:]
        out.append((field, direction))
    return out


def apply_sorts(query, sorts: List[Tuple[str, str]],
                default_field=None, tie_breaker=None):
    """
    Apply an ORDER BY to the SQLAlchemy query.

    - sorts: list of (field, direction) from parse_sort
    - default_field: a column to use if 'sorts' is empty (e.g., Task.created_at)
    - tie_breaker: a column appended at the end for stable ordering (e.g., Task.id)
    """
    # Map allowed fields to actual columns
    columns = {
        "id": Task.id,
        "title": Task.title,
        "status": Task.status,
        "priority": Task.priority,
        "due_date": Task.due_date,
        "created_at": Task.created_at,
        "project_id": Task.project_id,
    }

    orders = []

    if not sorts and default_field is not None:
        # If you provide a default_field, assume DESC by convention for created_at-like fields.
        orders.append(desc(default_field))

    for field, direction in sorts:
        col = columns.get(field)
        if not col:
            continue

        if field in ("due_date",):  # ensure NULLS LAST when sorting by dates
            if direction == "desc":
                orders.append(nullslast(desc(col)))
            else:
                orders.append(nullslast(asc(col)))
        else:
            orders.append(desc(col) if direction == "desc" else asc(col))

    # Stable tie-breaker at the end
    if tie_breaker is not None:
        if all(getattr(o.element if hasattr(o, "element") else o, "key", None) != getattr(tie_breaker, "key", None)
               for o in orders):
            orders.append(desc(tie_breaker))

    if orders:
        query = query.order_by(*orders)
    return query


# ---------- Pagination ----------
def paginate_query(query, page: int, per_page: int) -> Tuple[List[Any], Dict[str, int]]:
    """Apply offset/limit and return items + meta block."""
    total = query.order_by(None).count()  # drop ORDER BY for accurate COUNT
    pages = max(1, math.ceil(total / per_page)) if total else 1
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    meta = {"page": page, "per_page": per_page, "total": total, "pages": pages}
    return items, meta


# ---------- Simple serializers (used by routes) ----------
def project_to_dict(p: Project) -> Dict[str, Any]:
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
    }


def task_to_dict(t: Task) -> Dict[str, Any]:
    return {
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "project_id": t.project_id,
        "priority": t.priority,
        "due_date": t.due_date.isoformat() if getattr(t, "due_date", None) else None,
        "created_at": t.created_at.isoformat() if getattr(t, "created_at", None) else None,
    }


def subtask_to_dict(s: Subtask) -> Dict[str, Any]:
    return {
        "id": s.id,
        "title": s.title,
        "status": s.status,
        "task_id": s.task_id,
        "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
    }