from django.urls import path

from apps.catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("c/<slug:slug>/", views.category_detail, name="category"),
    path("p/<slug:slug>/", views.product_detail, name="product"),
]
