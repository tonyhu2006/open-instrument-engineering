"""
Administration serializers (§15.2, §15.3, §15.7).
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.viewsets import ServiceModelSerializer

from .access import effective_permissions
from .models import Organization, ProjectTaskForce, Role, TaskForceMembership

User = get_user_model()


# =============================================================================
# Organization
# =============================================================================


class OrganizationSerializer(ServiceModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "description",
            "logo",
            "settings",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"slug": {"required": False}}


class OrganizationListSerializer(ServiceModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "code", "slug", "name", "is_active"]


# =============================================================================
# Roles
# =============================================================================


class RoleSerializer(ServiceModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "organization",
            "code",
            "name",
            "level",
            "level_display",
            "description",
            "permissions",
            "is_system_role",
            "display_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_system_role", "created_at", "updated_at"]


class RoleListSerializer(ServiceModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "level",
            "level_display",
            "organization",
            "organization_name",
            "permissions",
            "is_system_role",
            "display_order",
        ]


# =============================================================================
# Users
# =============================================================================

_USER_PROFILE_FIELDS = [
    "phone",
    "department",
    "title",
    "employee_id",
    "language",
    "timezone",
]


class UserSerializer(ServiceModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )
    role_name = serializers.CharField(source="role.name", read_only=True, default=None)
    role_code = serializers.CharField(source="role.code", read_only=True, default=None)
    role_level = serializers.IntegerField(
        source="role.level", read_only=True, default=None
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "organization",
            "organization_name",
            "role",
            "role_name",
            "role_code",
            "role_level",
            "is_superuser",
            "is_staff",
            *_USER_PROFILE_FIELDS,
            "avatar",
            "is_active",
            "date_joined",
            "last_login",
        ]
        # Superuser/staff flags are not grantable through the API; the
        # Administrator role carries the authority (§15.2).
        read_only_fields = [
            "id",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
        ]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username


class MeSerializer(UserSerializer):
    """Current user + effective permission matrix (drives the UI)."""

    permissions = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["permissions"]
        read_only_fields = UserSerializer.Meta.fields + ["permissions"]

    @extend_schema_field(
        serializers.DictField(
            child=serializers.ListField(child=serializers.CharField())
        )
    )
    def get_permissions(self, obj):
        return effective_permissions(obj)


class UserListSerializer(ServiceModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source="role.name", read_only=True, default=None)
    role_code = serializers.CharField(source="role.code", read_only=True, default=None)
    role_level = serializers.IntegerField(
        source="role.level", read_only=True, default=None
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "organization",
            "organization_name",
            "role",
            "role_name",
            "role_code",
            "role_level",
            "is_superuser",
            "is_active",
        ]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username


class UserCreateSerializer(ServiceModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "organization",
            "role",
            *_USER_PROFILE_FIELDS,
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"role": {"required": True, "allow_null": False}}

    def validate(self, attrs):
        if attrs["password"] != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class StatusMessageSerializer(serializers.Serializer):
    status = serializers.CharField()


class PreferencesSerializer(serializers.Serializer):
    """I18N-04 / ADM-06 user preferences. Unknown keys are UI preferences
    (e.g. ``tableWidths``) and are deep-merged on PATCH."""

    language = serializers.CharField(required=False)
    timezone = serializers.CharField(required=False)
    date_format = serializers.CharField(required=False)
    number_format = serializers.CharField(required=False)


# =============================================================================
# Task forces
# =============================================================================


class ProjectTaskForceSerializer(ServiceModelSerializer):
    leader_name = serializers.CharField(
        source="leader.username", read_only=True, default=None
    )
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True, default=None
    )
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTaskForce
        fields = [
            "id",
            "project_id",
            "code",
            "name",
            "description",
            "leader",
            "leader_name",
            "created_by",
            "created_by_name",
            "created_by_role",
            "member_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_by_role",
            "created_at",
            "updated_at",
        ]

    def get_member_count(self, obj) -> int:
        return obj.memberships.filter(is_active=True).count()


class TaskForceMembershipSerializer(ServiceModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.SerializerMethodField()
    task_force_name = serializers.CharField(source="task_force.name", read_only=True)
    role_in_project_name = serializers.CharField(
        source="role_in_project.name", read_only=True, default=None
    )
    added_by_name = serializers.CharField(
        source="added_by.username", read_only=True, default=None
    )

    class Meta:
        model = TaskForceMembership
        fields = [
            "id",
            "user",
            "user_name",
            "user_full_name",
            "task_force",
            "task_force_name",
            "role_in_project",
            "role_in_project_name",
            "joined_at",
            "added_by",
            "added_by_name",
            "is_active",
        ]
        read_only_fields = fields

    def get_user_full_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username


class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_in_project = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False, allow_null=True
    )


class AssignProjectSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(allow_null=True)


class MyTaskForceSerializer(ServiceModelSerializer):
    """Entry of GET /api/v1/me/task-forces/."""

    project_no = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTaskForce
        fields = ["id", "code", "name", "project_id", "project_no", "project_name"]

    def get_project_no(self, obj) -> str | None:
        project = obj.project
        return project.project_no if project else None

    def get_project_name(self, obj) -> str | None:
        project = obj.project
        return project.name if project else None
