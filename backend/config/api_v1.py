"""
``/api/v1/`` routes — SPECIFICATION §4.2.1 / §5.4, decisions D1–D3.

All resources are flat under ``/api/v1/<resource>/`` (D2). Tenant-scoped
resources need the ``X-Project-ID`` header; public ones are listed in
``apps.tenants.middleware.PUBLIC_ONLY_PREFIXES``.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.administration.views import (
    MeViewSet,
    OrganizationViewSet,
    ProjectTaskForceViewSet,
    RoleViewSet,
    UserViewSet,
)
from apps.audit.views import AuditLogViewSet
from apps.core import views as core_views
from apps.core.auth import LoginView, RefreshView
from apps.core_engineering.views import (
    ClientViewSet,
    InstrumentTypeViewSet,
    LoopViewSet,
    NamingConventionViewSet,
    PlantHierarchyViewSet,
    PlantViewSet,
    SiteViewSet,
    TagNumberViewSet,
    TagViewSet,
)
from apps.tenants.views import ProjectTenantViewSet

router = DefaultRouter()
# --- public schema (§15.7, §15.1.3) ---
router.register("me", MeViewSet, basename="me")
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("task-forces", ProjectTaskForceViewSet, basename="task-force")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("tenants/projects", ProjectTenantViewSet, basename="project")
# --- tenant schema (§5.4.3, §5.4.4, §15.7) ---
router.register("clients", ClientViewSet, basename="client")
router.register("sites", SiteViewSet, basename="site")
router.register("plants", PlantViewSet, basename="plant")
router.register("plant-hierarchy", PlantHierarchyViewSet, basename="plant-hierarchy")
router.register("loops", LoopViewSet, basename="loop")
router.register("instrument-types", InstrumentTypeViewSet, basename="instrument-type")
router.register("instruments", TagViewSet, basename="instrument")
router.register(
    "naming-conventions", NamingConventionViewSet, basename="naming-convention"
)
router.register("tags", TagNumberViewSet, basename="tag-number")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("health/", core_views.health_check, name="health-check"),
    path("", include(router.urls)),
]
