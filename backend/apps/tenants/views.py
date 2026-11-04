"""
Project tenant API — §15.1.3.

Permissions (§15.2.4 "Project" row): Administrator CRUD, PM/PE read+update,
everyone else read; visibility limited by §15.3.3.
"""

from django_tenants.utils import get_public_schema_name
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.administration.access import user_accessible_project_ids
from apps.administration.permissions import RoleMatrixPermission
from apps.core.viewsets import ServiceModelViewSet

from .models import ProjectTenant
from .serializers import ProjectTenantCreateSerializer, ProjectTenantSerializer
from .services import ProjectTenantService


class ProjectTenantViewSet(ServiceModelViewSet):
    """Engineering projects (one PostgreSQL schema each)."""

    queryset = ProjectTenant.objects.exclude(schema_name=get_public_schema_name())
    service_class = ProjectTenantService
    permission_classes = [RoleMatrixPermission]
    rbac_resource = "project"
    rbac_action_map = {"switch": "read", "current": "read"}
    filterset_fields = ["status", "organization_id"]
    search_fields = ["project_no", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        accessible = user_accessible_project_ids(self.request.user)
        if accessible is None:
            return queryset
        return queryset.filter(pk__in=accessible)

    def get_serializer_class(self):
        if self.action == "create":
            return ProjectTenantCreateSerializer
        return ProjectTenantSerializer

    @extend_schema(
        request=None,
        responses=inline_serializer(
            "ProjectSwitchResponse",
            {"message": serializers.CharField(), "project": ProjectTenantSerializer()},
        ),
    )
    @action(detail=True, methods=["post"])
    def switch(self, request, pk=None):
        """Confirm access to the project. Tenant selection itself is
        per-request via the ``X-Project-ID`` header (ADM-T01)."""
        project = self.get_object()
        return Response(
            {
                "message": f"Switched to project {project.project_no}",
                "project": ProjectTenantSerializer(project).data,
            }
        )

    @extend_schema(
        responses=inline_serializer(
            "CurrentProjectResponse",
            {"project": ProjectTenantSerializer(allow_null=True)},
        ),
    )
    @action(detail=False, methods=["get"])
    def current(self, request):
        """The project selected by ``X-Project-ID`` (if any)."""
        raw = request.headers.get("X-Project-ID")
        project = None
        if raw and raw.isdigit():
            project = self.get_queryset().filter(pk=int(raw)).first()
        return Response(
            {"project": ProjectTenantSerializer(project).data if project else None}
        )
