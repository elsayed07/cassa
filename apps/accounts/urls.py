from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("orders/", views.order_list, name="order-list"),
    path("orders/<uuid:order_id>/", views.order_detail, name="order-detail"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("addresses/", views.address_list, name="address-list"),
    path("addresses/add/", views.address_add, name="address-add"),
    path("addresses/<uuid:pk>/edit/", views.address_edit, name="address-edit"),
    path("addresses/<uuid:pk>/delete/", views.address_delete, name="address-delete"),
]
