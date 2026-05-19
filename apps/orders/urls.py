from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("confirm/", views.order_confirm, name="confirm"),
    path("<str:order_number>/", views.order_success, name="success"),
]
