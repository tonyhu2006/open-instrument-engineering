"""
Tenant Middleware - Header-based tenant selection for API access.

Instead of using subdomains, we use a custom header (X-Project-ID) to select the tenant.
This is more suitable for SPA applications with a single domain.
"""

from django.db import connection
from django.http import JsonResponse
from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name

from .models import ProjectTenant


def _user_accessible_project_ids(user):
    """Lazy import to avoid Django app-loading race at module import time."""
    from apps.administration.access import user_accessible_project_ids
    return user_accessible_project_ids(user)


class HeaderBasedTenantMiddleware(TenantMainMiddleware):
    """
    Middleware that selects tenant based on X-Project-ID header.
    
    For API requests:
    - If X-Project-ID header is present, switch to that project's schema
    - If no header, use public schema (for shared resources like auth)
    
    For admin requests:
    - Use public schema
    """
    
    TENANT_HEADER = 'HTTP_X_PROJECT_ID'
    
    def _get_public_tenant(self):
        """Return a lightweight tenant-like object representing the public schema.

        django-tenants templatetags expect request.tenant to have a `schema_name`
        attribute, so we cannot use None here.
        """
        public_schema = get_public_schema_name()
        try:
            return ProjectTenant.objects.get(schema_name=public_schema)
        except ProjectTenant.DoesNotExist:
            # Fallback: create a simple object with the required attribute
            class _PublicTenant:
                schema_name = public_schema
                domain_url = ''
            return _PublicTenant()

    # Paths that MUST run in the public schema regardless of any X-Project-ID
    # header. These manage shared-schema resources (tenant CRUD, auth, users,
    # organizations, roles, audit logs) so routing them to a tenant schema
    # causes django-tenants' TenantSyncRouter to block writes and raises 500.
    PUBLIC_ONLY_PREFIXES = (
        '/admin/',
        '/api/token',
        '/api/tenants/',       # ProjectTenant CRUD — creates schemas
        '/api/admin/',         # Users, orgs, roles, audit logs (public schema)
    )

    def process_request(self, request):
        # Routes that always run in the public schema (ignore any X-Project-ID)
        if any(request.path.startswith(p) for p in self.PUBLIC_ONLY_PREFIXES):
            connection.set_schema_to_public()
            request.tenant = self._get_public_tenant()
            return
        
        # Check for project ID in header
        project_id = request.META.get(self.TENANT_HEADER)
        
        if project_id:
            try:
                tenant = ProjectTenant.objects.get(pk=project_id)
                connection.set_tenant(tenant)
                request.tenant = tenant
            except ProjectTenant.DoesNotExist:
                return JsonResponse(
                    {'error': f'Project with ID {project_id} not found'},
                    status=404
                )
            except Exception as e:
                return JsonResponse(
                    {'error': f'Error switching to project: {str(e)}'},
                    status=500
                )
        else:
            # No project specified - use public schema
            connection.set_schema_to_public()
            request.tenant = self._get_public_tenant()


class TenantContextMiddleware:
    """
    Additional middleware to add tenant context to the request.
    
    This middleware runs after authentication and adds:
    - request.current_project: The current ProjectTenant (if any)
    - request.available_projects: Projects the user has access to
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add current project from tenant
        request.current_project = getattr(request, 'tenant', None)

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            accessible = _user_accessible_project_ids(user)
            if accessible is None:
                # Administrator / superuser: all projects
                request.available_projects = ProjectTenant.objects.all()
            else:
                request.available_projects = ProjectTenant.objects.filter(pk__in=accessible)

            # Validate X-Project-ID: if a non-public tenant is selected, the
            # user MUST be a member / leader of that project (SPECIFICATION
            # §3.1.0.5.6). Administrators bypass via accessible == None.
            current = request.current_project
            public_schema = get_public_schema_name()
            if (
                accessible is not None
                and current is not None
                and getattr(current, 'schema_name', None) != public_schema
                and getattr(current, 'pk', None) is not None
                and current.pk not in accessible
            ):
                # Reset schema to public so the request does not leak data
                connection.set_schema_to_public()
                return JsonResponse(
                    {'error': 'You are not a member of this project.'},
                    status=403,
                )
        else:
            request.available_projects = ProjectTenant.objects.none()

        return self.get_response(request)
