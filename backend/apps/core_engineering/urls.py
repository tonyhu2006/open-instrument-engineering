"""
Core Engineering URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PlantHierarchyViewSet,
    LoopViewSet,
    InstrumentTypeViewSet,
    TagViewSet,
)

app_name = "core_engineering"

router = DefaultRouter()
router.register(r"hierarchy", PlantHierarchyViewSet, basename="hierarchy")
router.register(r"loops", LoopViewSet, basename="loop")
router.register(r"instrument-types", InstrumentTypeViewSet, basename="instrument-type")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
]
