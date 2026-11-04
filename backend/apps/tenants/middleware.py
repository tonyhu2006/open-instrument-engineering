"""
Tenant middleware — X-Project-ID header routing (ADM-T01 / ADM-T03 / §15.3.3).

* ``HeaderBasedTenantMiddleware`` selects the schema from ``X-Project-ID``.
  A malformed, unknown or public-schema id is rejected with **403** and the
  connection is reset to the public schema (§15.3.3 / DoD #10).
* ``TenantContextMiddleware`` (after authentication) exposes
  ``request.current_project`` / ``request.available_projects`` and enforces
  project membership for session-authenticated users. JWT users are checked
  by ``IsProjectMemberOrPublicSchema`` inside DRF.
"""

from django.db import connection
from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name

from apps.core.exceptions import error_response

from .models import ProjectTenant

API_PREFIX = "/api/v1/"

# Endpoints that manage public-schema resources: always served from the
# public schema, whatever X-Project-ID says.
PUBLIC_ONLY_PREFIXES = (
    "/admin/",
    "/api/token",  # deprecated auth alias (decision D1)
    "/api/schema/",
    "/api/docs/",
    "/api/redoc/",
    f"{API_PREFIX}auth/",
    f"{API_PREFIX}health/",
    f"{API_PREFIX}me/",
    f"{API_PREFIX}tenants/",
    f"{API_PREFIX}organizations/",
    f"{API_PREFIX}roles/",
    f"{API_PREFIX}users/",
    f"{API_PREFIX}task-forces/",
    f"{API_PREFIX}audit-logs/",
)

FORBIDDEN_CODE = "AUTH_PROJECT_FORBIDDEN"
FORBIDDEN_MESSAGE = "You are not a member of this project."


def _user_accessible_project_ids(user):
    """Lazy import to avoid an app-loading cycle."""
    from apps.administration.access import user_accessible_project_ids

    return user_accessible_project_ids(user)


class _PublicTenant:
    """Stand-in for the public schema when no public ProjectTenant row exists
    (django-tenants code expects ``request.tenant.schema_name``)."""

    pk = None
    domain_url = ""

    def __init__(self):
        self.schema_name = get_public_schema_name()


def _forbidden(request, message=FORBIDDEN_MESSAGE):
    connection.set_schema_to_public()
    request.tenant = HeaderBasedTenantMiddleware.public_tenant()
    return error_response(FORBIDDEN_CODE, message, 403, request=request)


class HeaderBasedTenantMiddleware(TenantMainMiddleware):
    TENANT_HEADER = "HTTP_X_PROJECT_ID"
    PUBLIC_ONLY_PREFIXES = PUBLIC_ONLY_PREFIXES

    @staticmethod
    def public_tenant():
        public_schema = get_public_schema_name()
        tenant = ProjectTenant.objects.filter(schema_name=public_schema).first()
        return tenant or _PublicTenant()

    def process_request(self, request):
        connection.set_schema_to_public()
        if any(request.path.startswith(p) for p in self.PUBLIC_ONLY_PREFIXES):
            request.tenant = self.public_tenant()
            return None

        raw = request.META.get(self.TENANT_HEADER)
        if raw is None or raw == "":
            request.tenant = self.public_tenant()
            return None

        raw = raw.strip()
        if not raw.isdigit():
            return _forbidden(request, "Invalid X-Project-ID header.")
        tenant = (
            ProjectTenant.objects.filter(pk=int(raw))
            .exclude(schema_name=get_public_schema_name())
            .first()
        )
        if tenant is None:
            # Do not reveal whether the project exists (§15.3.3).
            return _forbidden(request)
        connection.set_tenant(tenant)
        request.tenant = tenant
        return None


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current = getattr(request, "tenant", None)
        public_schema = get_public_schema_name()
        is_project = (
            current is not None
            and getattr(current, "schema_name", None) != public_schema
            and getattr(current, "pk", None) is not None
        )
        request.current_project = current if is_project else None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            accessible = _user_accessible_project_ids(user)
            if accessible is None:
                request.available_projects = ProjectTenant.objects.exclude(
                    schema_name=public_schema
                )
            else:
                request.available_projects = ProjectTenant.objects.filter(
                    pk__in=accessible
                )
                if is_project and current.pk not in accessible:
                    return _forbidden(request)
        else:
            request.available_projects = ProjectTenant.objects.none()

        return self.get_response(request)
