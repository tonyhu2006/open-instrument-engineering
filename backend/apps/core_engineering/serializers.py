"""
Core engineering serializers. All expose the §4.1.1 audit columns and
``row_version`` (read-only) plus write-only ``expected_row_version`` (§4.1.3).
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.viewsets import VersionedModelSerializer as Base

from .models import (
    Client,
    InstrumentType,
    Loop,
    NamingConvention,
    Plant,
    PlantHierarchy,
    Site,
    Tag,
)

RO = list(Base.BASE_READ_ONLY)
BASE = list(Base.BASE_FIELDS)

# =============================================================================
# Hierarchy (§15.4)
# =============================================================================


class ClientSerializer(Base):
    class Meta:
        model = Client
        fields = BASE + [
            "code",
            "name",
            "contact_person",
            "contact_email",
            "contact_phone",
            "address",
        ]
        read_only_fields = RO


class SiteSerializer(Base):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Site
        fields = BASE + [
            "client",
            "client_name",
            "code",
            "name",
            "location",
            "address",
            "timezone",
        ]
        read_only_fields = RO

    def validate_client(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("Client has been deleted.")
        return value


class PlantSerializer(Base):
    site_name = serializers.CharField(source="site.name", read_only=True)
    site_code = serializers.CharField(source="site.code", read_only=True)
    root_node = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = BASE + [
            "site",
            "site_name",
            "site_code",
            "code",
            "name",
            "description",
            "capacity",
            "is_active",
            "root_node",
        ]
        read_only_fields = RO

    @extend_schema_field(OpenApiTypes.INT)
    def get_root_node(self, obj):
        root = PlantHierarchy.alive.filter(plant=obj, parent__isnull=True).first()
        return root.pk if root else None

    def validate_site(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("Site has been deleted.")
        return value


class PlantHierarchySerializer(Base):
    parent_name = serializers.CharField(
        source="parent.name", read_only=True, default=None
    )
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = PlantHierarchy
        fields = BASE + [
            "plant",
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
        ]
        read_only_fields = RO + ["level"]
        extra_kwargs = {
            "parent": {"required": False, "allow_null": True},
            "plant": {"required": False, "allow_null": True},
        }

    @extend_schema_field(OpenApiTypes.INT)
    def get_children_count(self, obj):
        return obj.get_children().filter(is_deleted=False).count()


class PlantHierarchyTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = PlantHierarchy
        fields = [
            "id",
            "plant",
            "name",
            "code",
            "node_type",
            "description",
            "is_active",
            "row_version",
            "children",
        ]

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_children(self, obj):
        children = obj.get_children().filter(is_deleted=False)
        return PlantHierarchyTreeSerializer(children, many=True).data


class HierarchyMoveSerializer(serializers.Serializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=PlantHierarchy.alive.all(), help_text="New parent node"
    )
    expected_row_version = serializers.IntegerField(required=False, min_value=1)


# =============================================================================
# Instrument index
# =============================================================================


class LoopSerializer(Base):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Loop
        fields = BASE + [
            "loop_tag",
            "function",
            "suffix",
            "unit",
            "unit_name",
            "unit_code",
            "description",
            "is_active",
            "tags_count",
        ]
        read_only_fields = RO

    @extend_schema_field(OpenApiTypes.INT)
    def get_tags_count(self, obj):
        return obj.tags.filter(is_deleted=False).count()

    def validate_unit(self, value):
        if value.is_deleted or value.node_type != PlantHierarchy.NodeType.UNIT:
            raise serializers.ValidationError(
                "Loop must be assigned to an existing UNIT node."
            )
        return value


class InstrumentTypeSerializer(Base):
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentType
        fields = BASE + [
            "name",
            "code",
            "category",
            "description",
            "schema_template",
            "default_spec_data",
            "is_active",
            "tags_count",
        ]
        read_only_fields = RO

    @extend_schema_field(OpenApiTypes.INT)
    def get_tags_count(self, obj):
        return obj.tags.filter(is_deleted=False).count()


class InstrumentTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = ["id", "name", "code", "category", "is_active", "row_version"]


class TagSerializer(Base):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    loop_tag = serializers.CharField(
        source="loop.loop_tag", read_only=True, default=None
    )
    instrument_type_name = serializers.CharField(
        source="instrument_type.name", read_only=True
    )
    instrument_type_code = serializers.CharField(
        source="instrument_type.code", read_only=True
    )
    full_tag = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = BASE + [
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
            "full_tag",
        ]
        read_only_fields = RO

    def validate_unit(self, value):
        if value.is_deleted or value.node_type != PlantHierarchy.NodeType.UNIT:
            raise serializers.ValidationError(
                "Tag must be assigned to an existing UNIT node."
            )
        return value

    def validate_loop(self, value):
        if value is not None and value.is_deleted:
            raise serializers.ValidationError("Loop has been deleted.")
        return value


class TagListSerializer(serializers.ModelSerializer):
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    loop_tag = serializers.CharField(
        source="loop.loop_tag", read_only=True, default=None
    )
    instrument_type_code = serializers.CharField(
        source="instrument_type.code", read_only=True
    )

    class Meta:
        model = Tag
        fields = [
            "id",
            "tag_number",
            "unit",
            "unit_code",
            "loop",
            "loop_tag",
            "instrument_type",
            "instrument_type_code",
            "service",
            "status",
            "row_version",
            "updated_at",
        ]


# =============================================================================
# Naming conventions (§15.5) and tag numbers (§15.7)
# =============================================================================


class NamingConventionSerializer(Base):
    hierarchy_format_display = serializers.CharField(
        source="get_hierarchy_format_display", read_only=True
    )

    class Meta:
        model = NamingConvention
        fields = BASE + [
            "name",
            "entity_type",
            "hierarchy_format",
            "hierarchy_format_display",
            "pattern",
            "pattern_template",
            "segment_definitions",
            "separator",
            "description",
            "examples",
            "validation_message",
            "is_active",
            "is_default",
            "priority",
        ]
        read_only_fields = RO


class NamingTemplateSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    entity_type = serializers.CharField()
    hierarchy_format = serializers.CharField()
    pattern_template = serializers.CharField()
    pattern = serializers.CharField()
    examples = serializers.ListField(child=serializers.CharField())
    segments = serializers.ListField(child=serializers.DictField())


class FromTemplateSerializer(serializers.Serializer):
    template = serializers.ChoiceField(choices=[])
    name = serializers.CharField(required=False, max_length=200)
    is_default = serializers.BooleanField(required=False, default=False)

    def __init__(self, *args, **kwargs):
        from .naming import PRESET_TEMPLATES

        super().__init__(*args, **kwargs)
        self.fields["template"].choices = [t["code"] for t in PRESET_TEMPLATES]


class ConventionTestSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=100)
    unit_id = serializers.IntegerField(required=False)


class NumberValidateSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=100)
    unit_id = serializers.IntegerField(required=False)
    instrument_type_id = serializers.IntegerField(required=False)
    entity_type = serializers.ChoiceField(
        choices=NamingConvention.EntityType.choices, default="TAG"
    )
    naming_convention_id = serializers.IntegerField(required=False)


class NumberParseSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=100)
    entity_type = serializers.ChoiceField(
        choices=NamingConvention.EntityType.choices, default="TAG"
    )
    naming_convention_id = serializers.IntegerField(required=False)


class NumberGenerateSerializer(serializers.Serializer):
    unit_id = serializers.IntegerField()
    instrument_type_id = serializers.IntegerField(required=False)
    entity_type = serializers.ChoiceField(
        choices=[("TAG", "Tag"), ("LOOP", "Loop")], default="TAG"
    )
    naming_convention_id = serializers.IntegerField(required=False)


class NamingResultSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    number = serializers.CharField()
    segments = serializers.DictField(child=serializers.CharField())
    errors = serializers.ListField(child=serializers.DictField())
    naming_convention_id = serializers.IntegerField(allow_null=True)
    expected_pattern = serializers.CharField(allow_null=True)
    message = serializers.CharField()


class GeneratedNumberSerializer(serializers.Serializer):
    generated_number = serializers.CharField()
    segments = serializers.DictField(child=serializers.CharField())
    next_sequence = serializers.IntegerField()
    naming_convention_id = serializers.IntegerField()
