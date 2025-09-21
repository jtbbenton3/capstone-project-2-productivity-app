# utils/pagination.py
def paginate(query, page=1, per_page=10, serializer=lambda x: x):
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    pages = (total + per_page - 1) // per_page if per_page else 1
    return {
        "data": [serializer(i) for i in items],
        "meta": {
            "page": page,
            "pages": pages,
            "total": total,
            "per_page": per_page,
        },
    }