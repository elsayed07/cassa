from django.http import JsonResponse
from django.urls import path


def health(request):  # type: ignore[return]
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", health, name="health"),
]
