"""
Core Engineering Serializers - DRF serializers for all models
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import Client, Site, Plant, PlantHierarchy, Loop, InstrumentType, Tag, NamingConvention


# =============================================================================
# Client, Site, Plant Serializers (Tenant-specific)
# =============================================================================

class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model (tenant-specific)."""
    
    class Meta:
        model = Client
        fields = [
            "id", "code", "name", "contact_person", "contact_email",
            "contact_phone", "address", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SiteSerializer(serializers.ModelSerializer):
    """Serializer for Site model (tenant-specific)."""
    
    client_name = serializers.CharField(source="client.name", read_only=True)
    
    class Meta:
        model = Site
        fields = [
            "id", "client", "client_name", "code", "name",
            "location", "address", "timezone", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlantSerializer(serializers.ModelSerializer):
    """Serializer for Plant model (tenant-specific)."""
    
    site_name = serializers.CharField(source="site.name", read_only=True)
    site_code = serializers.CharField(source="site.code", read_only=True)
    
    class Meta:
        model = Plant
        fields = [
            "id", "site", "site_name", "site_code", "code", "name",
            "description", "capacity", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NamingConventionSerializer(serializers.ModelSerializer):
    """Serializer for NamingConvention model (tenant-specific)."""
    
    hierarchy_format_display = serializers.CharField(
        source="get_hierarchy_format_display", read_only=True
    )
    
    class Meta:
        model = NamingConvention
        fields = [
            "id", "name", "description", "hierarchy_format", "hierarchy_format_display",
            "regex_pattern", "segment_definitions", "example_tags",
            "is_default", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# PlantHierarchy Serializers
# =============================================================================

class PlantHierarchySerializer(serializers.ModelSerializer):
    """Serializer for PlantHierarchy model."""

    parent_name = serializers.CharField(source="parent.name", read_only=True)
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = PlantHierarchy
        fields = [
            "id",
            "name",
            "code",
            "node_type",
            "parent",
            "parent_name",
            "description",
            "is_active",
            "full_path",
            "children_count",
            "level",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "level", "created_at", "updated_at"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make parent not required for root nodes (PLANT type)
        self.fields['parent'].required = False
        self.fields['parent'].allow_null = True

    @extend_schema_field(OpenApiTypes.INT)
    def get_children_count(self, obj):
        return obj.get_children().count()


class PlantHierarchyTreeSerializer(serializers.ModelSerializer):
    """Serializer for PlantHierarchy tree structure with nested children."""

    children = serializers.SerializerMethodField()

    class Meta:
        model = PlantHierarchy
        fields = [
            "id",
            "name",
            "code",
            "node_type",
            "description",
            "is_active",
            "children",
        ]

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_children(self, obj):
        children = obj.get_children()
        return PlantHierarchyTreeSerializer(children, many=True).data


class LoopSerializer(serializers.ModelSerializer):
    """Serializer for Loop model."""

    unit_name = serializers.CharField(source="unit.name", read_only=True)
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Loop
        fields = [
            "id",
            "loop_tag",
            "function",
            "suffix",
            "unit",
            "unit_name",
            "unit_code",
            "description",
            "is_active",
            "tags_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_tags_count(self, obj):
        return obj.tags.count()

    def validate_unit(self, value):
        """Ensure unit is of type UNIT."""
        if value.node_type != PlantHierarchy.NodeType.UNIT:
            raise serializers.ValidationError(
                "Loop must be assigned to a UNIT, not a PLANT or AREA."
            )
        return value


class InstrumentTypeSerializer(serializers.ModelSerializer):
    """Serializer for InstrumentType model."""

    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentType
        fields = [
            "id",
            "name",
            "code",
            "category",
            "description",
            "schema_template",
            "default_spec_data",
            "is_active",
            "tags_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_tags_count(self, obj):
        return obj.tags.count()


class InstrumentTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for InstrumentType listing."""

    class Meta:
        model = InstrumentType
        fields = ["id", "name", "code", "category", "is_active"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    unit_name = serializers.CharField(source="unit.name", read_only=True)
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    loop_tag = serializers.CharField(source="loop.loop_tag", read_only=True)
    instrument_type_name = serializers.CharField(
        source="instrument_type.name", read_only=True
    )
    instrument_type_code = serializers.CharField(
        source="instrument_type.code", read_only=True
    )
    full_tag = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            "id",
            "tag_number",
            "unit",
            "unit_name",
            "unit_code",
            "loop",
            "loop_tag",
            "instrument_type",
            "instrument_type_name",
            "instrument_type_code",
            "service",
            "description",
            "spec_data",
            "status",
            "revision",
            "full_tag",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "revision", "created_at", "updated_at"]

    def validate_unit(self, value):
        """Ensure unit is of type UNIT."""
        if value.node_type != PlantHierarchy.NodeType.UNIT:
            raise serializers.ValidationError(
                "Tag must be assigned to a UNIT, not a PLANT or AREA."
            )
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        unit = attrs.get("unit", getattr(self.instance, "unit", None))
        loop = attrs.get("loop", getattr(self.instance, "loop", None))
        instrument_type = attrs.get(
            "instrument_type", getattr(self.instance, "instrument_type", None)
        )
        spec_data = attrs.get("spec_data", getattr(self.instance, "spec_data", {}))

        # Validate loop belongs to the same unit
        if loop and unit:
            if loop.unit_id != unit.id:
                raise serializers.ValidationError(
                    {
                        "loop": f"Loop must belong to the same unit as the tag. "
                        f"Tag unit: {unit.code}, Loop unit: {loop.unit.code}"
                    }
                )

        # Validate spec_data against instrument_type schema
        if instrument_type and spec_data:
            is_valid, errors = instrument_type.validate_spec_data(spec_data)
            if not is_valid:
                raise serializers.ValidationError(
                    {"spec_data": f"Validation failed: {'; '.join(errors)}"}
                )

        return attrs


class TagListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Tag listing (grid view)."""

    unit_code = serializers.CharField(source="unit.code", read_only=True)
    loop_tag = serializers.CharField(source="loop.loop_tag", read_only=True)
    instrument_type_code = serializers.CharField(
        source="instrument_type.code", read_only=True
    )

    class Meta:
        model = Tag
        fields = [
            "id",
            "tag_number",
            "unit_code",
            "loop_tag",
            "instrument_type_code",
            "service",
            "status",
            "revision",
        ]


class TagBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating tags."""

    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of tag IDs to update",
    )
    status = serializers.ChoiceField(
        choices=Tag.Status.choices,
        required=False,
        help_text="New status for all selected tags",
    )
    loop = serializers.PrimaryKeyRelatedField(
        queryset=Loop.objects.all(),
        required=False,
        allow_null=True,
        help_text="New loop for all selected tags",
    )
