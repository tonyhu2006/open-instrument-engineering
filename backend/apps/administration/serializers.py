"""
Administration Serializers - API serialization for administration models

Note: Project, Client, Site, Plant, NamingConvention serializers have been moved to:
- Project → apps.tenants.serializers
- Client, Site, Plant, NamingConvention → apps.core_engineering.serializers (tenant schema)
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Organization,
    Role,
    ProjectMembership,
    ProjectTaskForce,
    TaskForceMembership,
    AuditLog,
)

User = get_user_model()


# =============================================================================
# Organization Serializers
# =============================================================================

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    class Meta:
        model = Organization
        fields = [
            "id", "code", "name", "description", "logo",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Organization list views."""
    
    class Meta:
        model = Organization
        fields = ["id", "code", "name", "is_active"]


# =============================================================================
# RBAC Serializers
# =============================================================================

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    
    class Meta:
        model = Role
        fields = [
            "id", "organization", "code", "name", "level", "level_display",
            "description", "permissions", "is_system_role",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Role list views."""
    
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    
    class Meta:
        model = Role
        fields = ["id", "code", "name", "level", "level_display"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    role_name = serializers.CharField(source="role.name", read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "full_name",
            "organization", "organization_name", "role", "role_name",
            "phone", "department", "title", "language", "timezone",
            "avatar", "is_active", "date_joined", "last_login"
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for User list views."""
    
    full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source="role.name", read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "role_name", "is_active"]
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password_confirm",
            "first_name", "last_name", "organization", "role",
            "phone", "department", "title", "language", "timezone"
        ]
    
    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectMembershipSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMembership model."""
    
    user_name = serializers.CharField(source="user.username", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    
    class Meta:
        model = ProjectMembership
        fields = [
            "id", "user", "user_name", "project_id",
            "role", "role_name", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Project Task Force Serializers
# =============================================================================

class ProjectTaskForceSerializer(serializers.ModelSerializer):
    """Serializer for ProjectTaskForce model."""
    
    leader_name = serializers.CharField(source="leader.username", read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectTaskForce
        fields = [
            "id", "project_id", "code", "name", "description",
            "leader", "leader_name", "member_count", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_member_count(self, obj):
        return obj.memberships.count()


class TaskForceMembershipSerializer(serializers.ModelSerializer):
    """Serializer for TaskForceMembership model."""
    
    user_name = serializers.CharField(source="user.username", read_only=True)
    task_force_name = serializers.CharField(source="task_force.name", read_only=True)
    
    class Meta:
        model = TaskForceMembership
        fields = [
            "id", "user", "user_name", "task_force", "task_force_name",
            "role", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Note: NamingConvention Serializers moved to apps.core_engineering.serializers
# =============================================================================


# =============================================================================
# Audit Log Serializers
# =============================================================================

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    user_name = serializers.CharField(source="user.username", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            "id", "organization", "project_id", "user", "user_name",
            "action", "action_display", "model_name", "object_id",
            "object_repr", "old_values", "new_values",
            "ip_address", "user_agent", "timestamp"
        ]
        read_only_fields = fields


# =============================================================================
# Note: Hierarchy Serializers moved to apps.core_engineering.serializers
# =============================================================================
