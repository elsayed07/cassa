from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.catalog.selectors import CategorySelector, ProductSelector
from shared.pagination import paginate


def home(request: HttpRequest) -> HttpResponse:
    featured = ProductSelector.featured()[:12]
    categories = CategorySelector.active_roots()
    return render(request, "pages/catalog/home.html", {
        "featured_products": featured,
        "categories": categories,
    })


def category_detail(request: HttpRequest, slug: str) -> HttpResponse:
    from shared.exceptions import NotFoundError
    from django.http import Http404

    try:
        category = CategorySelector.by_slug(slug)
    except NotFoundError:
        raise Http404

    products_qs = ProductSelector.by_category(category)
    page = int(request.GET.get("page", 1))
    result = paginate(products_qs, page=page)

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/product_grid.html", result)

    return render(request, "pages/catalog/category.html", {
        "category": category,
        "breadcrumbs": list(category.get_ancestors(include_self=True)),
        **result,
    })


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    from shared.exceptions import NotFoundError
    from django.http import Http404

    try:
        product = ProductSelector.by_slug(slug)
    except NotFoundError:
        raise Http404

    from apps.recommendations.services import RecommendationService
    from apps.reviews.selectors import ReviewSelector

    recommendations = RecommendationService.for_product(str(product.id))
    reviews = ReviewSelector.approved_for_product(product)
    review_summary = ReviewSelector.aggregate(product)

    return render(request, "pages/catalog/product.html", {
        "product": product,
        "variants": product.variants.filter(is_active=True),
        "recommendations": recommendations,
        "reviews": reviews,
        "review_summary": review_summary,
    })


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    result: dict = {"query": query, "items": [], "total_count": 0}

    if query:
        products_qs = ProductSelector.search(query)
        page = int(request.GET.get("page", 1))
        result = {"query": query, **paginate(products_qs, page=page)}

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/product_grid.html", result)

    return render(request, "pages/catalog/search.html", result)
