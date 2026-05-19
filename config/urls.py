from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_prometheus import exports as prometheus_exports

from api.v1 import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("metrics/", prometheus_exports.ExportToDjangoView, name="prometheus-django-metrics"),
    path("webhooks/", include("apps.payments.webhook_urls")),
    path("accounts/", include("allauth.urls")),
    path("health/", include("apps.analytics.health_urls")),
]

urlpatterns += i18n_patterns(
    path("", include("apps.catalog.urls")),
    path("cart/", include("apps.carts.urls")),
    path("checkout/", include("apps.orders.urls")),
    path("account/", include("apps.accounts.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
