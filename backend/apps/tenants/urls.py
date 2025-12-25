"""
Tenant URLs - API routes for project tenant management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectTenantViewSet, ProjectDomainViewSet

router = DefaultRouter()
router.register(r'projects', ProjectTenantViewSet, basename='project')
router.register(r'domains', ProjectDomainViewSet, basename='domain')

urlpatterns = [
    path('', include(router.urls)),
]
