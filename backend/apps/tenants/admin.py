from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import ProjectTenant


@admin.register(ProjectTenant)
class ProjectTenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['project_no', 'name', 'schema_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project_no', 'name', 'schema_name']
    readonly_fields = ['schema_name', 'created_at', 'updated_at']


# NOTE: ProjectDomain is intentionally NOT registered in Django admin.
# This project uses header-based tenant routing (X-Project-ID) via
# apps.tenants.middleware.HeaderBasedTenantMiddleware — the ProjectDomain
# model is only kept because django-tenants requires TENANT_DOMAIN_MODEL
# to be set in settings.py. It has no runtime role. Managing domains in
# the admin UI would only confuse operators.
