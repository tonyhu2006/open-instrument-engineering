"""
ViewSet base classes that route writes through the service layer.
"""

from __future__ import annotations

from django_tenants.utils import get_public_schema_name
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, viewsets
from rest_framework.validators import UniqueValidator

from .exceptions import ServiceError
from .models import SoftDeleteModel
from .services import CrudService


class ServiceModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet whose create/update/destroy delegate to ``service_class``.

    * soft-deleted rows are hidden from every read;
    * ``expected_row_version`` (body for PUT/PATCH, query string for DELETE)
      drives the optimistic lock (§4.1.3).
    """

    service_class: type[CrudService] = CrudService

    def get_service(self) -> CrudService:
        service = self.service_class(request=self.request)
        if service.model is None:
            service.model = self.get_queryset().model
        return service

    def get_queryset(self):
        queryset = super().get_queryset()
        if issubclass(queryset.model, SoftDeleteModel):
            queryset = queryset.filter(is_deleted=False)
        return queryset

    def perform_create(self, serializer):
        serializer.instance = self.get_service().create(serializer.validated_data)

    def perform_update(self, serializer):
        serializer.instance = self.get_service().update(
            serializer.instance, serializer.validated_data
        )

    def perform_destroy(self, instance):
        self.get_service().delete(
            instance,
            expected_row_version=self.request.query_params.get("expected_row_version"),
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "expected_row_version",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=False,
                description="Optimistic lock: current row_version (§4.1.3).",
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TenantScopedViewSetMixin:
    """Reject tenant-data requests that did not select a project.

    Without an ``X-Project-ID`` header the request runs in the public schema,
    where tenant tables do not exist; answer 400 instead of a database error.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        tenant = getattr(request, "tenant", None)
        schema = getattr(tenant, "schema_name", None)
        if not schema or schema == get_public_schema_name():
            raise ServiceError(
                "This endpoint requires a project context: send the "
                "X-Project-ID header.",
                code="AUTH_PROJECT_REQUIRED",
            )


class TenantModelViewSet(TenantScopedViewSetMixin, ServiceModelViewSet):
    """Service-backed ViewSet for tenant-schema business tables."""


class ServiceModelSerializer(serializers.ModelSerializer):
    """Serializer for service-backed writes.

    Uniqueness is validated by the model (``full_clean``) inside the service
    so that business rules run first and violations surface with their
    §4.2.6 error codes (e.g. ``IDX_TAG_DUPLICATE``) instead of DRF's generic
    unique messages.
    """

    def get_validators(self):
        return []

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        validators = field_kwargs.get("validators")
        if validators:
            field_kwargs["validators"] = [
                v for v in validators if not isinstance(v, UniqueValidator)
            ]
        return field_class, field_kwargs


class VersionedModelSerializer(ServiceModelSerializer):
    """Adds the write-only ``expected_row_version`` field (§4.1.3) and the
    read-only audit columns (§4.1.1) to tenant business serializers."""

    expected_row_version = serializers.IntegerField(
        write_only=True,
        required=False,
        min_value=1,
        help_text="Required on update: the row_version the client last read.",
    )

    BASE_READ_ONLY = (
        "id",
        "row_version",
        "created_at",
        "created_by_id",
        "updated_at",
        "updated_by_id",
    )
    BASE_FIELDS = BASE_READ_ONLY + ("expected_row_version",)
