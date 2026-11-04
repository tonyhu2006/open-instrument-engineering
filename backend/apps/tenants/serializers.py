"""
ProjectTenant serializers (§15.1.3 / §15.4.1).
"""

from rest_framework import serializers

from .models import ProjectTenant


class ProjectTenantSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTenant
        fields = [
            "id",
            "project_no",
            "name",
            "schema_name",
            "organization_id",
            "organization_name",
            "description",
            "status",
            "start_date",
            "end_date",
            "hierarchy_config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project_no",
            "schema_name",
            "created_at",
            "updated_at",
        ]

    def get_organization_name(self, obj) -> str | None:
        from apps.administration.models import Organization

        org = Organization.objects.filter(pk=obj.organization_id).first()
        return org.name if org else None


class ProjectTenantCreateSerializer(serializers.ModelSerializer):
    """Create a project; the schema name derives from ``project_no``."""

    class Meta:
        model = ProjectTenant
        fields = [
            "id",
            "project_no",
            "name",
            "schema_name",
            "organization_id",
            "description",
            "status",
            "start_date",
            "end_date",
            "hierarchy_config",
        ]
        read_only_fields = ["id", "schema_name"]
        extra_kwargs = {
            "organization_id": {"required": False},
            "project_no": {"validators": []},
        }

    def validate_project_no(self, value):
        if ProjectTenant.objects.filter(project_no=value).exists():
            raise serializers.ValidationError("Project number already exists.")
        schema = ProjectTenant.schema_name_for(value)
        if ProjectTenant.objects.filter(schema_name=schema).exists():
            raise serializers.ValidationError(
                f"Another project already maps to schema '{schema}'."
            )
        return value

    def to_representation(self, instance):
        return ProjectTenantSerializer(instance, context=self.context).data
