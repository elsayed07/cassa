from __future__ import annotations

from typing import Any

from django.core.paginator import EmptyPage, Paginator


def paginate(
    queryset: Any,
    page: int = 1,
    page_size: int = 24,
) -> dict[str, Any]:
    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        "items": list(page_obj.object_list),
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "total_count": paginator.count,
        "has_next": page_obj.has_next(),
        "has_prev": page_obj.has_previous(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "prev_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
    }
