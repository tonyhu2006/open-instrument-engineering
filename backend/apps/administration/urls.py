"""
Administration URL Configuration

Note: Project, Client, Site, Plant, NamingConvention routes have been moved to:
- Projects → /api/tenants/projects/
- Client, Site, Plant → /api/engineering/ (tenant-specific)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrganizationViewSet,
    RoleViewSet,
    UserViewSet,
    ProjectMembershipViewSet,
    ProjectTaskForceViewSet,
    TaskForceMembershipViewSet,
    AuditLogViewSet,
)

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")
router.register(r"project-memberships", ProjectMembershipViewSet, basename="project-membership")
router.register(r"task-forces", ProjectTaskForceViewSet, basename="task-force")
router.register(r"task-force-memberships", TaskForceMembershipViewSet, basename="task-force-membership")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
