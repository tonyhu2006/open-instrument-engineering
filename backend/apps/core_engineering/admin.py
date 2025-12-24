"""
Core Engineering Admin Configuration
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import PlantHierarchy, Loop, InstrumentType, Tag


@admin.register(PlantHierarchy)
class PlantHierarchyAdmin(DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "node_type",
        "code",
        "is_active",
    )
    list_display_links = ("indented_title",)
    list_filter = ("node_type", "is_active")
    search_fields = ("name", "code", "description")


@admin.register(Loop)
class LoopAdmin(admin.ModelAdmin):
    list_display = ("loop_tag", "function", "suffix", "unit", "is_active")
    list_filter = ("function", "is_active", "unit")
    search_fields = ("loop_tag", "description")
    raw_id_fields = ("unit",)


@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "code", "description")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "tag_number",
        "instrument_type",
        "unit",
        "loop",
        "service",
        "status",
    )
    list_filter = ("status", "instrument_type", "unit")
    search_fields = ("tag_number", "service", "description")
    raw_id_fields = ("unit", "loop", "instrument_type")
