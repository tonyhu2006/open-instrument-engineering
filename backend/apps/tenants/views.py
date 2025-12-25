"""
Tenant Views - API views for project tenant management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import connection

from .models import ProjectTenant, ProjectDomain
from .serializers import (
    ProjectTenantSerializer,
    ProjectTenantCreateSerializer,
    ProjectDomainSerializer,
)


class ProjectTenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ProjectTenants (projects with schema isolation).
    
    list: Get all projects the user has access to
    create: Create a new project (creates new schema)
    retrieve: Get project details
    update: Update project metadata
    destroy: Delete project (drops schema)
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter projects by user's organization."""
        user = self.request.user
        if user.is_superuser:
            return ProjectTenant.objects.all()
        
        if hasattr(user, 'organization_id') and user.organization_id:
            return ProjectTenant.objects.filter(organization_id=user.organization_id)
        
        return ProjectTenant.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectTenantCreateSerializer
        return ProjectTenantSerializer
    
    def perform_create(self, serializer):
        """Create project and its schema."""
        # Set organization from user if not provided
        if 'organization_id' not in serializer.validated_data:
            serializer.validated_data['organization_id'] = self.request.user.organization_id
        
        # Save creates the tenant and schema
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def switch(self, request, pk=None):
        """
        Switch to this project's schema.
        Returns project details and sets the schema for subsequent requests.
        """
        project = self.get_object()
        connection.set_tenant(project)
        
        return Response({
            'message': f'Switched to project {project.project_no}',
            'project': ProjectTenantSerializer(project).data,
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current project context."""
        tenant = getattr(request, 'tenant', None)
        if tenant:
            return Response({
                'project': ProjectTenantSerializer(tenant).data,
            })
        return Response({
            'project': None,
            'message': 'No project selected (using public schema)',
        })


class ProjectDomainViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ProjectDomains."""
    
    queryset = ProjectDomain.objects.all()
    serializer_class = ProjectDomainSerializer
    permission_classes = [IsAuthenticated]
