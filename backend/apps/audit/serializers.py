from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "organization",
            "project_id",
            "user",
            "user_name",
            "action",
            "action_display",
            "model_name",
            "object_id",
            "object_repr",
            "old_values",
            "new_values",
            "changed_fields",
            "change_details",
            "batch_id",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = fields
