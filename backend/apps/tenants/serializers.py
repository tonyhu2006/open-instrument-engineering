"""
Tenant Serializers - API serializers for project tenant management.
"""

from rest_framework import serializers
from .models import ProjectTenant, ProjectDomain


class ProjectTenantSerializer(serializers.ModelSerializer):
    """Serializer for ProjectTenant (project with schema isolation)."""
    
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectTenant
        fields = [
            'id', 'project_no', 'name', 'schema_name',
            'organization_id', 'organization_name',
            'description', 'status', 'start_date', 'end_date',
            'hierarchy_config', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'schema_name', 'created_at', 'updated_at']
    
    def get_organization_name(self, obj):
        from apps.administration.models import Organization
        org = Organization.objects.filter(pk=obj.organization_id).first()
        return org.name if org else None


class ProjectTenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new ProjectTenant."""
    
    class Meta:
        model = ProjectTenant
        fields = [
            'project_no', 'name', 'organization_id',
            'description', 'status', 'start_date', 'end_date',
            'hierarchy_config',
        ]
    
    def validate_project_no(self, value):
        if ProjectTenant.objects.filter(project_no=value).exists():
            raise serializers.ValidationError("Project number already exists.")
        return value


class ProjectDomainSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDomain."""
    
    class Meta:
        model = ProjectDomain
        fields = ['id', 'domain', 'tenant', 'is_primary']
