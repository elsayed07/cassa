from django.urls import path

from apps.carts import views

app_name = "carts"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/", views.add_to_cart, name="add"),
    path("update/", views.update_cart, name="update"),
    path("remove/", views.remove_from_cart, name="remove"),
    path("coupon/apply/", views.apply_coupon, name="coupon-apply"),
    path("coupon/remove/", views.remove_coupon, name="coupon-remove"),
]
