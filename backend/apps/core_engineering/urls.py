"""
Core Engineering URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ClientViewSet,
    SiteViewSet,
    PlantViewSet,
    NamingConventionViewSet,
    PlantHierarchyViewSet,
    LoopViewSet,
    InstrumentTypeViewSet,
    TagViewSet,
)

app_name = "core_engineering"

router = DefaultRouter()
# Tenant-specific hierarchy models
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"plants", PlantViewSet, basename="plant")
router.register(r"naming-conventions", NamingConventionViewSet, basename="naming-convention")
# Engineering models
router.register(r"hierarchy", PlantHierarchyViewSet, basename="hierarchy")
router.register(r"loops", LoopViewSet, basename="loop")
router.register(r"instrument-types", InstrumentTypeViewSet, basename="instrument-type")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
]
