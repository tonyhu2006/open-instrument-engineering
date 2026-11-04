"""
Tenant URLs - API routes for project tenant management.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectTenantViewSet

router = DefaultRouter()
router.register(r"projects", ProjectTenantViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
]
