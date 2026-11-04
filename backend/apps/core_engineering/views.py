"""
Core engineering API (tenant schema; requires ``X-Project-ID``).

Endpoints follow §5.4.3 (plant hierarchy), §5.4.4 (instruments / loops /
instrument types) and §15.7 (naming conventions, tag numbers). Writes go
through services (§4.1.14) and are authorized by the RBAC matrix (§15.2.4).
"""

import django_filters
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.administration.permissions import (
    IsProjectMemberOrPublicSchema,
    RoleMatrixPermission,
)
from apps.core.exceptions import ServiceError
from apps.core.viewsets import TenantModelViewSet, TenantScopedViewSetMixin

from . import naming
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
from .serializers import (
    ClientSerializer,
    ConventionTestSerializer,
    FromTemplateSerializer,
    GeneratedNumberSerializer,
    HierarchyMoveSerializer,
    InstrumentTypeListSerializer,
    InstrumentTypeSerializer,
    LoopSerializer,
    NamingConventionSerializer,
    NamingResultSerializer,
    NamingTemplateSerializer,
    NumberGenerateSerializer,
    NumberParseSerializer,
    NumberValidateSerializer,
    PlantHierarchySerializer,
    PlantHierarchyTreeSerializer,
    PlantSerializer,
    SiteSerializer,
    TagListSerializer,
    TagSerializer,
)
from .services import (
    ClientService,
    InstrumentTypeService,
    LoopService,
    NamingConventionService,
    PlantHierarchyService,
    PlantService,
    SiteService,
    TagService,
)

ENGINEERING_PERMISSIONS = [
    IsAuthenticated,
    IsProjectMemberOrPublicSchema,
    RoleMatrixPermission,
]


class EngineeringViewSet(TenantModelViewSet):
    permission_classes = ENGINEERING_PERMISSIONS


# =============================================================================
# Project hierarchy (§5.4.3)
# =============================================================================


class ClientViewSet(EngineeringViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    service_class = ClientService
    rbac_resource = "plant_hierarchy"
    search_fields = ["code", "name"]
    ordering = ["name"]


class SiteViewSet(EngineeringViewSet):
    queryset = Site.objects.select_related("client").all()
    serializer_class = SiteSerializer
    service_class = SiteService
    rbac_resource = "plant_hierarchy"
    filterset_fields = ["client"]
    search_fields = ["code", "name", "location"]
    ordering = ["code"]


class PlantViewSet(EngineeringViewSet):
    queryset = Plant.objects.select_related("site").all()
    serializer_class = PlantSerializer
    service_class = PlantService
    rbac_resource = "plant_hierarchy"
    filterset_fields = ["site", "is_active"]
    search_fields = ["code", "name"]
    ordering = ["code"]


class PlantHierarchyViewSet(EngineeringViewSet):
    """MPTT tree. ``?tree=true`` returns the nested tree (§5.4.3)."""

    queryset = PlantHierarchy.objects.select_related("parent", "plant").all()
    serializer_class = PlantHierarchySerializer
    service_class = PlantHierarchyService
    rbac_resource = "plant_hierarchy"
    rbac_action_map = {"move": "update"}
    filterset_fields = ["node_type", "is_active", "parent", "plant"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["tree_id", "lft"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "tree",
                OpenApiTypes.BOOL,
                description="Return the nested tree of live root nodes.",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        if request.query_params.get("tree") in ("1", "true", "True"):
            roots = (
                PlantHierarchy.objects.root_nodes()
                .filter(is_deleted=False)
                .order_by("code")
            )
            plant = request.query_params.get("plant")
            if plant:
                roots = roots.filter(plant_id=plant)
            return Response(PlantHierarchyTreeSerializer(roots, many=True).data)
        return super().list(request, *args, **kwargs)

    @extend_schema(request=HierarchyMoveSerializer, responses=PlantHierarchySerializer)
    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        node = self.get_object()
        serializer = HierarchyMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        moved = self.get_service().move(
            node,
            serializer.validated_data["parent"],
            expected_row_version=serializer.validated_data.get("expected_row_version"),
        )
        return Response(PlantHierarchySerializer(moved).data)


# =============================================================================
# Instrument index (§5.4.4)
# =============================================================================


class LoopViewSet(EngineeringViewSet):
    queryset = Loop.objects.select_related("unit").all()
    serializer_class = LoopSerializer
    service_class = LoopService
    rbac_resource = "loop"
    rbac_action_map = {"tags": "read"}
    filterset_fields = ["function", "is_active", "unit"]
    search_fields = ["loop_tag", "description"]
    ordering_fields = ["loop_tag", "function", "created_at"]
    ordering = ["loop_tag"]

    @extend_schema(responses=TagListSerializer(many=True))
    @action(detail=True, methods=["get"])
    def tags(self, request, pk=None):
        """Instruments of this loop (§5.4.4 ``/loops/{id}/tags/``)."""
        loop = self.get_object()
        tags = loop.tags.filter(is_deleted=False).select_related(
            "unit", "instrument_type", "loop"
        )
        return Response(TagListSerializer(tags, many=True).data)


class InstrumentTypeViewSet(EngineeringViewSet):
    queryset = InstrumentType.objects.all()
    service_class = InstrumentTypeService
    rbac_resource = "instrument_type"
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["code", "name", "category", "created_at"]
    ordering = ["code"]

    def get_serializer_class(self):
        if self.action == "list":
            return InstrumentTypeListSerializer
        return InstrumentTypeSerializer


class TagFilter(django_filters.FilterSet):
    """Filter by any hierarchy level (ADM-02): client / site / plant /
    area or unit node (``node`` includes the whole subtree)."""

    client = django_filters.NumberFilter(field_name="unit__plant__site__client")
    site = django_filters.NumberFilter(field_name="unit__plant__site")
    plant = django_filters.NumberFilter(field_name="unit__plant")
    node = django_filters.NumberFilter(method="filter_node")

    class Meta:
        model = Tag
        fields = ["status", "unit", "loop", "instrument_type"]

    def filter_node(self, queryset, name, value):
        node = PlantHierarchy.objects.filter(pk=value).first()
        if node is None:
            return queryset.none()
        units = node.get_descendants(include_self=True).values("pk")
        return queryset.filter(unit__in=units)


class TagViewSet(EngineeringViewSet):
    """Instrument tags — ``/api/v1/instruments/`` (§5.4.4)."""

    queryset = Tag.objects.select_related(
        "unit", "unit__plant", "loop", "instrument_type"
    ).all()
    service_class = TagService
    rbac_resource = "tag"
    filterset_class = TagFilter
    search_fields = ["tag_number", "service", "description", "loop__loop_tag"]
    ordering_fields = [
        "tag_number",
        "status",
        "row_version",
        "created_at",
        "updated_at",
    ]
    ordering = ["tag_number"]

    def get_serializer_class(self):
        if self.action == "list":
            return TagListSerializer
        return TagSerializer


# =============================================================================
# Naming conventions & tag numbers (§15.5 / §15.7)
# =============================================================================


def _unit_or_error(unit_id):
    if unit_id is None:
        return None
    unit = PlantHierarchy.alive.filter(
        pk=unit_id, node_type=PlantHierarchy.NodeType.UNIT
    ).first()
    if unit is None:
        raise ServiceError(
            "Unit not found.", code="ADM_UNIT_NOT_FOUND", field="unit_id"
        )
    return unit


def _convention_or_error(entity_type, convention_id=None):
    convention = naming.find_convention(entity_type, convention_id)
    if convention is None:
        raise ServiceError(
            "No active naming convention is configured for this entity type.",
            code="IDX_NAMING_CONVENTION_MISSING",
            field="naming_convention_id",
        )
    return convention


class NamingConventionViewSet(EngineeringViewSet):
    queryset = NamingConvention.objects.all()
    serializer_class = NamingConventionSerializer
    service_class = NamingConventionService
    rbac_resource = "naming_convention"
    rbac_action_map = {
        "set_default": "update",
        "validate_number": "read",
        "templates": "read",
        "from_template": "create",
    }
    filterset_fields = ["entity_type", "hierarchy_format", "is_default", "is_active"]
    search_fields = ["name"]
    ordering = ["entity_type", "-is_default", "priority", "name"]

    @extend_schema(request=None, responses=NamingConventionSerializer)
    @action(detail=True, methods=["post"], url_path="set-default")
    def set_default(self, request, pk=None):
        convention = self.get_service().set_default(self.get_object())
        return Response(NamingConventionSerializer(convention).data)

    @extend_schema(request=ConventionTestSerializer, responses=NamingResultSerializer)
    @action(detail=True, methods=["post"], url_path="validate")
    def validate_number(self, request, pk=None):
        """Test a number against this convention (§15.7 "验证测试")."""
        convention = self.get_object()
        serializer = ConventionTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = _unit_or_error(serializer.validated_data.get("unit_id"))
        result = naming.validate_number(
            convention,
            serializer.validated_data["number"],
            unit=unit,
            entity_type=convention.entity_type,
        )
        return Response(result.as_dict())

    @extend_schema(responses=NamingTemplateSerializer(many=True))
    @action(detail=False, methods=["get"])
    def templates(self, request):
        """§15.5.4 preset templates."""
        return Response(
            NamingTemplateSerializer(naming.PRESET_TEMPLATES, many=True).data
        )

    @extend_schema(
        request=FromTemplateSerializer, responses={201: NamingConventionSerializer}
    )
    @action(detail=False, methods=["post"], url_path="from-template")
    def from_template(self, request):
        serializer = FromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = naming.TEMPLATES_BY_CODE[serializer.validated_data["template"]]
        data = naming.template_defaults(template)
        if serializer.validated_data.get("name"):
            data["name"] = serializer.validated_data["name"]
        data["is_default"] = serializer.validated_data.get("is_default", False)
        convention = self.get_service().create(data)
        return Response(
            NamingConventionSerializer(convention).data, status=status.HTTP_201_CREATED
        )


class TagNumberViewSet(TenantScopedViewSetMixin, viewsets.GenericViewSet):
    """§15.7 ``/api/v1/tags/validate-number|generate-number|parse-number/``."""

    permission_classes = ENGINEERING_PERMISSIONS
    rbac_resource = "tag"
    rbac_action_map = {
        "validate_number": "read",
        "parse_number": "read",
        "generate_number": "read",
    }
    serializer_class = NumberValidateSerializer
    pagination_class = None

    @extend_schema(request=NumberValidateSerializer, responses=NamingResultSerializer)
    @action(detail=False, methods=["post"], url_path="validate-number")
    def validate_number(self, request):
        serializer = NumberValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        convention = _convention_or_error(
            data["entity_type"], data.get("naming_convention_id")
        )
        function_code = None
        if data.get("instrument_type_id"):
            itype = InstrumentType.alive.filter(pk=data["instrument_type_id"]).first()
            function_code = itype.code if itype else None
        result = naming.validate_number(
            convention,
            data["number"],
            unit=_unit_or_error(data.get("unit_id")),
            entity_type=data["entity_type"],
            function_code=function_code,
        )
        return Response(result.as_dict())

    @extend_schema(request=NumberParseSerializer, responses=NamingResultSerializer)
    @action(detail=False, methods=["post"], url_path="parse-number")
    def parse_number(self, request):
        serializer = NumberParseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        convention = _convention_or_error(
            data["entity_type"], data.get("naming_convention_id")
        )
        return Response(naming.parse_number(convention, data["number"]).as_dict())

    @extend_schema(
        request=NumberGenerateSerializer, responses=GeneratedNumberSerializer
    )
    @action(detail=False, methods=["post"], url_path="generate-number")
    def generate_number(self, request):
        serializer = NumberGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        convention = _convention_or_error(
            data["entity_type"], data.get("naming_convention_id")
        )
        unit = _unit_or_error(data["unit_id"])
        function_code = None
        if data.get("instrument_type_id"):
            itype = InstrumentType.alive.filter(
                Q(pk=data["instrument_type_id"])
            ).first()
            if itype is None:
                raise ServiceError(
                    "Instrument type not found.",
                    code="IDX_INSTRUMENT_TYPE_NOT_FOUND",
                    field="instrument_type_id",
                )
            function_code = itype.code
        try:
            result = naming.generate_number(
                convention, unit=unit, function_code=function_code
            )
        except naming.NamingGenerationError as exc:
            raise ServiceError(str(exc), code="IDX_NAMING_GENERATION_FAILED") from exc
        return Response(result)
