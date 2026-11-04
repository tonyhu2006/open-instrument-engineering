"""
URL configuration — every API lives under ``/api/v1/`` (decisions D1/D2).

Exempt (D2): ``/admin/`` (Django admin) and ``/api/docs|redoc|schema/``.
``/api/token/*`` is the deprecated authentication alias (D1).
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.auth import DeprecatedLoginView, DeprecatedRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_v1")),
    # Deprecated aliases (D1) — removed after one minor version.
    path("api/token/", DeprecatedLoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", DeprecatedRefreshView.as_view(), name="token_refresh"),
    # API documentation (exempt from the /api/v1 prefix)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
