from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import ProjectTenant, ProjectDomain


@admin.register(ProjectTenant)
class ProjectTenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['project_no', 'name', 'schema_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project_no', 'name', 'schema_name']
    readonly_fields = ['schema_name', 'created_at', 'updated_at']


@admin.register(ProjectDomain)
class ProjectDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain']
