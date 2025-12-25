"""
Administration Views - API endpoints for administration models

Note: Project, Client, Site, Plant, NamingConvention have been moved to tenant-specific apps.
- Project → apps.tenants (ProjectTenant)
- Client, Site, Plant, NamingConvention → apps.core_engineering (tenant schema)
"""

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Organization,
    Role,
    ProjectMembership,
    ProjectTaskForce,
    TaskForceMembership,
    AuditLog,
)
from .serializers import (
    OrganizationSerializer,
    OrganizationListSerializer,
    RoleSerializer,
    RoleListSerializer,
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    ProjectMembershipSerializer,
    ProjectTaskForceSerializer,
    TaskForceMembershipSerializer,
    AuditLogSerializer,
)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """API endpoint for Organization CRUD operations."""
    
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return OrganizationListSerializer
        return OrganizationSerializer


# Note: ProjectViewSet, ClientViewSet, SiteViewSet, PlantViewSet have been moved to:
# - ProjectViewSet → apps.tenants.views.ProjectTenantViewSet
# - ClientViewSet, SiteViewSet, PlantViewSet → apps.core_engineering.views (tenant schema)


class RoleViewSet(viewsets.ModelViewSet):
    """API endpoint for Role CRUD operations."""
    
    queryset = Role.objects.select_related("organization").all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["organization", "level", "is_system_role"]
    search_fields = ["code", "name"]
    ordering_fields = ["level", "name"]
    ordering = ["-level", "name"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer
    
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_system_role:
            return Response(
                {"error": "System roles cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for User CRUD operations."""
    
    queryset = User.objects.select_related("organization", "role").all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["organization", "role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["username"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "User activated."})
    
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "User deactivated."})


class ProjectMembershipViewSet(viewsets.ModelViewSet):
    """API endpoint for ProjectMembership CRUD operations."""
    
    queryset = ProjectMembership.objects.select_related("user", "role").all()
    serializer_class = ProjectMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["user", "project_id", "role", "is_active"]
    ordering = ["-created_at"]


class ProjectTaskForceViewSet(viewsets.ModelViewSet):
    """API endpoint for ProjectTaskForce CRUD operations."""
    
    queryset = ProjectTaskForce.objects.select_related("leader").all()
    serializer_class = ProjectTaskForceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["project_id", "is_active"]
    search_fields = ["code", "name"]
    ordering = ["code"]
    
    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        """Get task force members."""
        task_force = self.get_object()
        memberships = task_force.memberships.select_related("user").all()
        serializer = TaskForceMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the task force."""
        task_force = self.get_object()
        user_id = request.data.get("user_id")
        role = request.data.get("role", "member")
        
        if not user_id:
            return Response(
                {"error": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        membership, created = TaskForceMembership.objects.get_or_create(
            user=user,
            task_force=task_force,
            defaults={"role": role}
        )
        
        if not created:
            return Response(
                {"error": "User is already a member."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TaskForceMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        """Remove a member from the task force."""
        task_force = self.get_object()
        user_id = request.data.get("user_id")
        
        if not user_id:
            return Response(
                {"error": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted, _ = TaskForceMembership.objects.filter(
            user_id=user_id,
            task_force=task_force
        ).delete()
        
        if deleted == 0:
            return Response(
                {"error": "Membership not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({"status": "Member removed."})


class TaskForceMembershipViewSet(viewsets.ModelViewSet):
    """API endpoint for TaskForceMembership CRUD operations."""
    
    queryset = TaskForceMembership.objects.select_related(
        "user", "task_force"
    ).all()
    serializer_class = TaskForceMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["user", "task_force", "role"]
    ordering = ["-created_at"]


# Note: NamingConventionViewSet moved to apps.core_engineering.views (tenant schema)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for AuditLog read operations (read-only)."""
    
    queryset = AuditLog.objects.select_related("organization", "user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["organization", "project_id", "user", "action", "model_name"]
    search_fields = ["object_repr", "model_name"]
    ordering = ["-timestamp"]
