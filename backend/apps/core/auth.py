"""
Authentication endpoints — §5.4.1 / decision D1.

Canonical: ``/api/v1/auth/login/`` and ``/api/v1/auth/refresh/``.
``/api/token/`` and ``/api/token/refresh/`` remain as deprecated aliases for
one minor version: same views, ``Deprecation``/``Sunset`` response headers and
``deprecated: true`` in the OpenAPI schema.
"""

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# One minor-version grace period (D1). Update together with the removal plan.
SUNSET = "Sun, 31 Jan 2027 00:00:00 GMT"
SUCCESSOR = {
    "login": "/api/v1/auth/login/",
    "refresh": "/api/v1/auth/refresh/",
}


@extend_schema(tags=["auth"], summary="Obtain JWT access/refresh tokens")
class LoginView(TokenObtainPairView):
    pass


@extend_schema(tags=["auth"], summary="Refresh the JWT access token")
class RefreshView(TokenRefreshView):
    pass


class _DeprecatedAliasMixin:
    successor = ""

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Deprecation"] = "true"
        response["Sunset"] = SUNSET
        response["Link"] = f'<{self.successor}>; rel="successor-version"'
        return response


@extend_schema(tags=["auth"], deprecated=True, summary="Deprecated: use auth/login")
class DeprecatedLoginView(_DeprecatedAliasMixin, TokenObtainPairView):
    successor = SUCCESSOR["login"]


@extend_schema(tags=["auth"], deprecated=True, summary="Deprecated: use auth/refresh")
class DeprecatedRefreshView(_DeprecatedAliasMixin, TokenRefreshView):
    successor = SUCCESSOR["refresh"]
