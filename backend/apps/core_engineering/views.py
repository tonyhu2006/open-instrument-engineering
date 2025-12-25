"""
Core Engineering Views - DRF ViewSets for all models
"""

from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Client, Site, Plant, PlantHierarchy, Loop, InstrumentType, Tag, NamingConvention
from .serializers import (
    ClientSerializer,
    SiteSerializer,
    PlantSerializer,
    NamingConventionSerializer,
    PlantHierarchySerializer,
    PlantHierarchyTreeSerializer,
    LoopSerializer,
    InstrumentTypeSerializer,
    InstrumentTypeListSerializer,
    TagSerializer,
    TagListSerializer,
    TagBulkUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List all plant hierarchy nodes"),
    retrieve=extend_schema(summary="Get a specific hierarchy node"),
    create=extend_schema(summary="Create a new hierarchy node"),
    update=extend_schema(summary="Update a hierarchy node"),
    partial_update=extend_schema(summary="Partially update a hierarchy node"),
    destroy=extend_schema(summary="Delete a hierarchy node"),
)
class PlantHierarchyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PlantHierarchy model.
    Provides CRUD operations and tree structure endpoints.
    """

    queryset = PlantHierarchy.objects.all()
    serializer_class = PlantHierarchySerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["node_type", "is_active", "parent"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["tree_id", "lft"]

    @extend_schema(
        summary="Get plant hierarchy as tree",
        description="Returns the entire plant hierarchy as a nested tree structure",
    )
    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Return the hierarchy as a nested tree structure."""
        roots = PlantHierarchy.objects.root_nodes().filter(is_active=True)
        serializer = PlantHierarchyTreeSerializer(roots, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get all units",
        description="Returns all UNIT type nodes (for dropdowns)",
    )
    @action(detail=False, methods=["get"])
    def units(self, request):
        """Return all UNIT nodes for selection dropdowns."""
        units = PlantHierarchy.objects.filter(
            node_type=PlantHierarchy.NodeType.UNIT, is_active=True
        )
        serializer = PlantHierarchySerializer(units, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get children of a node",
        description="Returns direct children of a specific hierarchy node",
    )
    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Return direct children of a node."""
        node = self.get_object()
        children = node.get_children()
        serializer = PlantHierarchySerializer(children, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all loops"),
    retrieve=extend_schema(summary="Get a specific loop"),
    create=extend_schema(summary="Create a new loop"),
    update=extend_schema(summary="Update a loop"),
    partial_update=extend_schema(summary="Partially update a loop"),
    destroy=extend_schema(summary="Delete a loop"),
)
class LoopViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Loop model.
    Provides CRUD operations for control loops.
    """

    queryset = Loop.objects.select_related("unit").all()
    serializer_class = LoopSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["function", "is_active", "unit"]
    search_fields = ["loop_tag", "description"]
    ordering_fields = ["loop_tag", "function", "created_at"]
    ordering = ["loop_tag"]

    @extend_schema(
        summary="Get tags in this loop",
        description="Returns all tags belonging to this loop",
    )
    @action(detail=True, methods=["get"])
    def tags(self, request, pk=None):
        """Return all tags in this loop."""
        loop = self.get_object()
        tags = loop.tags.select_related("unit", "instrument_type").all()
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all instrument types"),
    retrieve=extend_schema(summary="Get a specific instrument type"),
    create=extend_schema(summary="Create a new instrument type"),
    update=extend_schema(summary="Update an instrument type"),
    partial_update=extend_schema(summary="Partially update an instrument type"),
    destroy=extend_schema(summary="Delete an instrument type"),
)
class InstrumentTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InstrumentType model.
    Provides CRUD operations for instrument type definitions.
    """

    queryset = InstrumentType.objects.all()
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["code", "name", "category", "created_at"]
    ordering = ["code"]

    def get_serializer_class(self):
        if self.action == "list":
            return InstrumentTypeListSerializer
        return InstrumentTypeSerializer

    @extend_schema(
        summary="Validate spec data against schema",
        description="Validates provided spec_data against this instrument type's schema_template",
        request={"application/json": {"type": "object"}},
        responses={200: {"type": "object", "properties": {"valid": {"type": "boolean"}, "errors": {"type": "array"}}}},
    )
    @action(detail=True, methods=["post"])
    def validate_spec(self, request, pk=None):
        """Validate spec_data against the instrument type's schema."""
        instrument_type = self.get_object()
        spec_data = request.data
        
        is_valid, errors = instrument_type.validate_spec_data(spec_data)
        return Response({"valid": is_valid, "errors": errors})


@extend_schema_view(
    list=extend_schema(summary="List all tags"),
    retrieve=extend_schema(summary="Get a specific tag"),
    create=extend_schema(summary="Create a new tag"),
    update=extend_schema(summary="Update a tag"),
    partial_update=extend_schema(summary="Partially update a tag"),
    destroy=extend_schema(summary="Delete a tag"),
)
class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tag model.
    Provides CRUD operations for instrument tags.
    """

    queryset = Tag.objects.select_related("unit", "loop", "instrument_type").all()
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "unit", "loop", "instrument_type"]
    search_fields = ["tag_number", "service", "description"]
    ordering_fields = ["tag_number", "status", "revision", "created_at", "updated_at"]
    ordering = ["tag_number"]

    def get_serializer_class(self):
        if self.action == "list":
            return TagListSerializer
        return TagSerializer

    @extend_schema(
        summary="Bulk update tags",
        description="Update multiple tags at once (status, loop assignment)",
        request=TagBulkUpdateSerializer,
        responses={200: {"type": "object", "properties": {"updated": {"type": "integer"}}}},
    )
    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """Bulk update multiple tags."""
        serializer = TagBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data["ids"]
        update_fields = {}
        
        if "status" in serializer.validated_data:
            update_fields["status"] = serializer.validated_data["status"]
        if "loop" in serializer.validated_data:
            update_fields["loop"] = serializer.validated_data["loop"]
        
        if not update_fields:
            return Response(
                {"error": "No fields to update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        updated = Tag.objects.filter(id__in=ids).update(**update_fields)
        return Response({"updated": updated})

    @extend_schema(
        summary="Search tags",
        description="Advanced search across multiple fields",
        parameters=[
            OpenApiParameter(name="q", description="Search query", required=True, type=str),
        ],
    )
    @action(detail=False, methods=["get"])
    def search(self, request):
        """Advanced search for tags."""
        query = request.query_params.get("q", "")
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=400)
        
        tags = Tag.objects.filter(
            Q(tag_number__icontains=query)
            | Q(service__icontains=query)
            | Q(description__icontains=query)
            | Q(loop__loop_tag__icontains=query)
        ).select_related("unit", "loop", "instrument_type")[:50]
        
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get tags by unit",
        description="Returns all tags in a specific unit",
        parameters=[
            OpenApiParameter(name="unit_id", description="Unit ID", required=True, type=int),
        ],
    )
    @action(detail=False, methods=["get"])
    def by_unit(self, request):
        """Get all tags in a specific unit."""
        unit_id = request.query_params.get("unit_id")
        if not unit_id:
            return Response(
                {"error": "unit_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        tags = Tag.objects.filter(unit_id=unit_id).select_related(
            "unit", "loop", "instrument_type"
        )
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data)


# =============================================================================
# Client, Site, Plant ViewSets (Tenant-specific)
# =============================================================================

class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Client model (tenant-specific data)."""
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["code", "name"]
    ordering = ["name"]


class SiteViewSet(viewsets.ModelViewSet):
    """ViewSet for Site model (tenant-specific data)."""
    
    queryset = Site.objects.select_related("client").all()
    serializer_class = SiteSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["client"]
    search_fields = ["code", "name", "location"]
    ordering = ["code"]


class PlantViewSet(viewsets.ModelViewSet):
    """ViewSet for Plant model (tenant-specific data)."""
    
    queryset = Plant.objects.select_related("site").all()
    serializer_class = PlantSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["site", "is_active"]
    search_fields = ["code", "name"]
    ordering = ["code"]


class NamingConventionViewSet(viewsets.ModelViewSet):
    """ViewSet for NamingConvention model (tenant-specific data)."""
    
    queryset = NamingConvention.objects.all()
    serializer_class = NamingConventionSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["hierarchy_format", "is_default", "is_active"]
    search_fields = ["name"]
    ordering = ["-is_default", "name"]
    
    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set this naming convention as the default."""
        convention = self.get_object()
        # Unset other defaults
        NamingConvention.objects.filter(is_default=True).update(is_default=False)
        convention.is_default = True
        convention.save()
        return Response({"status": "Set as default."})
