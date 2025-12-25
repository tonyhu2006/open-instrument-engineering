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
    
    def process_request(self, request):
        # Admin and auth endpoints always use public schema
        if request.path.startswith('/admin/') or request.path.startswith('/api/token'):
            connection.set_schema_to_public()
            request.tenant = None
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
            request.tenant = None


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
        
        # Add available projects for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # For now, return all projects the user's organization has access to
            # This can be refined based on ProjectMembership
            if hasattr(request.user, 'organization_id') and request.user.organization_id:
                request.available_projects = ProjectTenant.objects.filter(
                    organization_id=request.user.organization_id
                )
            else:
                request.available_projects = ProjectTenant.objects.none()
        else:
            request.available_projects = ProjectTenant.objects.none()
        
        response = self.get_response(request)
        return response
