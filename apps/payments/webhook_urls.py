from django.urls import path

from apps.payments import views

urlpatterns = [
    path("stripe/", views.stripe_webhook, name="stripe-webhook"),
]
